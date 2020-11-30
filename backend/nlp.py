from snownlp import SnowNLP

text1 = '垃圾东西，很难吃'


def rank_sentiments(sentiments):
    if sentiments >= 0.8:
        return 5
    elif sentiments >= 0.6:
        return 4
    elif sentiments >= 0.4:
        return 3
    elif sentiments >= 0.2:
        return 2
    else:
        return 1

s1 = SnowNLP(text1)


print(rank_sentiments(s1.sentiments))
