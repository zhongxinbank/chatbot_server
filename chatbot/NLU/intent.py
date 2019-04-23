# coding=utf-8

import jieba
import torch
from torch.autograd import Variable
import re
import os

from .data.data import prepare_sequence, preprocessing
from .model import Encoder, Decoder

class IntentInference(object):
    def __init__(self, stopwords, model_path="./chatbot/NLU/models", train_iob_path="./chatbot/NLU/data/processed_train_data.pkl"):
        self.stopwords = stopwords
        self.word2index, self.tag2index, self.intent2index = preprocessing(train_iob_path)
        self.index2intent = {v: k for k, v in self.intent2index.items()}
        self.encoder = Encoder(len(self.word2index), 64, 64)
        self.decoder = Decoder(len(self.tag2index), len(self.intent2index), len(self.tag2index) // 3, 64 * 2)
        self.encoder.load_state_dict(torch.load(os.path.join(model_path, "jointnlu-encoder.pkl"), map_location='cpu'))
        self.decoder.load_state_dict(torch.load(os.path.join(model_path, "jointnlu-decoder.pkl"), map_location='cpu'))
        self.encoder.eval()
        self.decoder.eval()

    def inference_sent(self, sentence, threshold=0.7):
        """
        main function
        :param sentence: str
        :param threshold: 0.7
        :return:
        """
        # 去除句子中的"\t"和"\n"特殊字符
        sentence = sentence.replace("\t", "")
        sentence = sentence.replace("\n", "")

        # 分词（加了自定义词典）
        # 去除stopwords
        # 替换NUMBER
        # 将分词后为空的sample跳过
        cut_list = []
        for word in jieba.cut(sentence):
            word = word.strip()
            if word and word not in self.stopwords:
                if re.search("^(\d+\.\d+|\d+)$", word):
                    cut_list.append("NUMBER")
                else:
                    cut_list.append(word)
        if cut_list:
            line = "BOS "
            for word in cut_list:
                line = line + word + " "
            line = line + "EOS\t"
            line = line + ("O " * (len(cut_list) + 1)) + "no_label" + "\n"
            label, value = self._inference_for_one_sentence(line)
            if value >= threshold:
                return {"label": label, "score": value}
            else:
                return {"label": "", "score": 0.0}
        else:
            return {"label": "", "score": 0.0}

    def _inference_for_one_sentence(self, line):
        test = [line]
        test = [t[:-1] for t in test]
        test = [[t.split("\t")[0].split(" "), t.split("\t")[1].split(" ")[:-1], t.split("\t")[1].split(" ")[-1]] for t
                in test]
        test = [[t[0][1:-1], t[1][1:], t[2]] for t in test]
        index = 0
        test_raw = test[index][0]
        test_in = prepare_sequence(test_raw, self.word2index)
        test_mask = Variable(torch.ByteTensor(tuple(map(lambda s: s == 0, test_in.data)))).view(1, -1)
        start_decode = Variable(torch.LongTensor([[self.word2index['<SOS>']] * 1])).transpose(1, 0)
        output, hidden_c = self.encoder(test_in.unsqueeze(0), test_mask.unsqueeze(0))
        tag_score, intent_score = self.decoder(start_decode, hidden_c, output, test_mask)
        intent_score = torch.softmax(intent_score, 1)
        v, i = torch.max(intent_score, 1)
        return self.index2intent[i.data.tolist()[0]], v.data.tolist()[0]


if __name__ == "__main__":
    config = {
        "stopwords_path": "./config/stopwords.txt",
        "user_dict_path": "./config/user_dict.txt",
        "train_iob_path": "./train.w-intent.iob",
        "model_path": "./models/"
    }
    intent_inference = IntentInference(config)
    while True:
        sent = input("user: ")
        print(intent_inference.inference_sent(sent))
