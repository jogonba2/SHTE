from StringProcessing import StringProcessing
from BuildVocabulary import BuildVocabulary
from HierarchicalTransformer import HierarchicalTransformer
from keras.utils.np_utils import to_categorical
import numpy as np

if __name__ == "__main__":

    document_max_sents = 30
    summary_max_sents = 4
    document_max_words_per_sent = 25
    summary_max_words_per_sent = 15
    embedding_dims = 64
    output_word_encoder_dims = [64, 64, 64] # Debe coincidir con los embeddings para las conexiones residuales
    output_sentence_encoder_dims = [64, 64, 64] # Debe coincidir con los embeddings para las conexiones residuales
    word_attention_dims = [16, 16, 16]
    sentence_attention_dims = [16, 16, 16]
    n_word_heads = [4, 4, 4]
    n_sentence_heads = [4, 4, 4]
    train_path = "./sample_set.csv"
    dev_path = "./sample_set.csv"
    max_vocabulary = 100

    # Build Vocabulary #
    #bv = BuildVocabulary()
    #string_processor = StringProcessing(train_path, dev_path)
    #print(string_processor.train)

    # Testing #

    max_vocabulary = 100
    n_samples = 5000

    x_pos_articles = np.random.randint(low = 1,
                                   high = 50,
                                   size = (n_samples, document_max_sents,
                                           document_max_words_per_sent)
                                   )

    x_pos_summaries = np.random.randint(low = 1,
                                   high = 50,
                                   size = (n_samples, summary_max_sents,
                                           summary_max_words_per_sent)
                                   )
    x_neg_articles = np.random.randint(low = 40,
                                   high = 90,
                                   size = (n_samples, document_max_sents,
                                           document_max_words_per_sent)
                                   )

    x_neg_summaries = np.random.randint(low = 40,
                                   high = 90,
                                   size = (n_samples, summary_max_sents,
                                           summary_max_words_per_sent)
                                   )

    x_articles = np.concatenate((x_pos_articles, x_neg_articles), axis=0)
    x_summaries = np.concatenate((x_pos_summaries, x_neg_summaries), axis=0)
    y = np.array([1 for i in range(n_samples)] + [0 for i in range(n_samples)])
    y = to_categorical(y, 2)
    print(x_articles.shape)
    print(x_summaries.shape)
    print(y.shape)

    # Training #
    ht = HierarchicalTransformer(max_vocabulary = max_vocabulary,
                                 document_max_sents = document_max_sents,
                                 summary_max_sents = summary_max_sents,
                                 document_max_words_per_sent = document_max_words_per_sent,
                                 summary_max_words_per_sent = summary_max_words_per_sent,
                                 embedding_dims = embedding_dims,
                                 output_word_encoder_dims = output_word_encoder_dims,
                                 output_sentence_encoder_dims = output_sentence_encoder_dims,
                                 word_attention_dims = word_attention_dims,
                                 sentence_attention_dims = sentence_attention_dims,
                                 n_word_heads = n_word_heads,
                                 n_sentence_heads = n_sentence_heads
                                )

    ht.build()
    print(ht.model.summary())
    ht.compile(ht.model)

    #ht.load(ht.model, "./first_version_weights.h5")
    #ht.model.fit([x_articles, x_summaries],
    #              y = y, batch_size = 64,
    #              epochs = 1, verbose = 1)

    #ht.save(ht.model, "./first_version_weights.h5")
    #print(ht.model.predict([]))
    ht.load(ht.model, "./first_version_weights.h5")

    # Visualize Attention #

    #x_article = np.random.randint(low=40, high=90,
    #                              size = (1, document_max_sents,
    #                                      document_max_words_per_sent))
    #np.save("sample.npy", x_article)

    x_article = np.load("sample.npy")
    attns = ht.attn_model.predict(x_article)[0] # (n cabezales ultimo encoder, n frases, n frases)
    attn_head_0 = attns[0]
    attn_head_1 = attns[1]
    attn_head_2 = attns[2]
    attn_head_3 = attns[3]

    import matplotlib.pyplot as plt

    print(sum(attn_head_0[0])) # = 1
    plt.imshow(attn_head_3, cmap='gray', interpolation='nearest')
    plt.colorbar()
    plt.show()

    # Mostrar la más clara y la más oscura, a ver qué pasa ahí
    print("MAS CLARA:", attn_head_2[:, 13], "\n")
    print("\n\n\n MAS OSCURA:", attn_head_2[:, 4], "\n")

    print("Palabras de la frase MAS CLARA:", x_article[0][13], "\n")
    print("\n\n\nPalabras de la frase MAS OSCURA:", x_article[0][4], "\n")

    #print(attn_head_0.shape)
    #print(attn_head_1.shape)

    # ¿Cual es la frase que más palabras entre 40 y 50 tiene?,
    # la que más tenga debe ser la que menos atención debe tener
    # porque el articulo de ejemplo generado pertenece a la clase negativa
    # (entre 40 y 90), y lo que le distingue de la clase positiva son los valores
    # que no están en el solapamiento con esta (entre 40 y 50)
    # La frase 4 y la 19 son las que menos atención tienen (las que menos aportan i.e. muchos valores entre 40 y 50).
    # Una de las dos debe ser la que más valores en el solapamiento tiene, según las atenciones (LO ES!)#
    # Lo mismo pero para las frases con valores mayores de 50, estas son las que más atención deben tener,
    # porque son las que más contribuyen a decir la clase negativa #
    # según las atenciones, las que más valores mayores de 50 tienen son las frases 8 y 13 (LO SON!)#

    counts = []
    for i in range(len(x_article[0])):
        counts.append(0)
        for j in range(len(x_article[0][i])):
            if 40 < x_article[0][i][j] < 50:
                counts[-1] += 1

    # Frase clavada! (4) #
    print("Frases con mayor solapamiento:" , [i for i,val in enumerate(counts) if val==max(counts)])

    # Frases clavadas! (8 y 13) #
    print("Frases con menor solapamiento:" , [i for i,val in enumerate(counts) if val==min(counts)])




    # Visualizing Positional Encodings #

    pos_encodings = np.zeros((50, 300))
    for i in range(50):
        for j in range(300):
            if j % 2 == 0:
                pos_encodings[i][j] = np.sin(i / (10000 ** ((2 * j) / 300)))
            else:
                pos_encodings[i][j] = np.cos(i / (10000 ** ((2 * j) / 300)))

    plt.imshow(pos_encodings.transpose(), interpolation='nearest')
    plt.colorbar()
    plt.show()