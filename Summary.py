import numpy as np
import networkx as nx

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from scipy.spatial.distance import cosine as cosine_distance

def ensure_nltk_resources():
    """
    Check and download necessary NLTK resources.
    """
    resources = {
        'tokenizers/punkt': 'punkt',
        'corpora/stopwords.zip': 'stopwords' 
    }
    for resource_path, resource_name in resources.items():
        try:
            nltk.data.find(resource_path) 
        except LookupError:
            nltk.download(resource_name) 

def preprocess_text(text):
    """
    Preprocess the input text: tokenize, remove punctuation, stopwords, and perform stemming.
    Returns: A list of tokenized sentences and a list of processed words after removing stopwords and stemming.
    """
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Remove punctuation and convert to lowercase
    tokenizer = RegexpTokenizer(r'\w+')
    words = tokenizer.tokenize(text.lower())

    # Remove stopwords from the list of words
    stop_words = set(stopwords.words('english') )
    words = [word for word in words if word not in stop_words]

    # Initialize the stemmer and stem the remaining words
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]

    return sentences, words

def sentence_similarity(sent1, sent2):
    """
    Compute the cosine similarity between two sentences.
    Returns: Cosine similarity score.
    """

    # Combine words from both sentences into a unique list
    all_words = list(set(sent1 + sent2))
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # Populate the vector for the first sentence
    for w in sent1:
        vector1[all_words.index(w)] += 1

    # Populate the vector for the second sentence
    for w in sent2:
        vector2[all_words.index(w)] += 1

    # Calculate and return the cosine similarity
    return 1 - cosine_distance(vector1, vector2)

def build_similarity_matrix(sentences):
    """
    Construct a similarity matrix for a list of sentences.
    Returns: 2D array representing the similarity between each pair of sentences.
    """
    # Initialize a similarity matrix with zeros
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
    
    # Populate the similarity matrix
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:  # Skip self-similarity
                similarity_matrix[i][j] = sentence_similarity(sentences[i], sentences[j])
    
    return similarity_matrix

def generate_summary(text, num_sentences):
    """
    Generate a summary of the input text based on the number of sentences specified.
    Returns: Summarized text.
    """
    # Preprocess the input text
    sentences, words = preprocess_text(text)
    if not sentences:
        return "Error: Text preprocessing failed."

    # Build a similarity matrix and create a graph from it
    sentence_similarity_matrix = build_similarity_matrix(sentences)
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)

    # Use PageRank algorithm to score sentences
    scores = nx.pagerank(sentence_similarity_graph)

    # Rank sentences based on scores and select the top sentences for the summary
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    summary = ' '.join([sentence for _, sentence in ranked_sentences[:num_sentences]])

    return summary

# Ensure that necessary NLTK resources are available
ensure_nltk_resources()

# Example Usage
text = "Your input text goes here."  # Replace with your actual input text
num_sentences = 3  # Number of sentences in the summary
summary = generate_summary(text, num_sentences) 
print(summary) 
