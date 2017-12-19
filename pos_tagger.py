import corpus_parser as cp

learningRate = 0.05
trainingEpochs = 1000

if __name__ == '__main__':
    print("Creating training data...")
    cp.runParser()
    print("Data created")
    # Need to generate a POS(POS)----(current POS(previous POS))----probability matrix first
    
    # Then generate a POS(word)----(current POS(current word))----probability matrix first

