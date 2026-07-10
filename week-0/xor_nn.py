import numpy as np
X = np.array([(0,0),(0,1),(1,0),(1,1)])
y = np.array([0, 1, 1, 0])
#print(X.shape)
#print(y.shape)

w1 = np.random.randn(2,4)
b1 = np.random.randn(4)
w2 = np.random.randn(4,1)
b2 = np.random.randn(1)

#print(w1)

def sigmoid(x):
    return 1/ (1 + np.exp(-x))

for epoch in range(10000):
    hidden_input = X @ w1 + b1
    #print(hidden_input)

    hidden_output = sigmoid(hidden_input)
    #print(hidden_output)

    output_input = hidden_output @ w2 + b2
    output = sigmoid(output_input)
    #print(output)

    loss = ((output - y.reshape(-1,1))** 2).mean()              #-1 :figure out based on actual size 1: column should be 1
    #print(loss)

    output_error = output - y.reshape(-1,1)
    output_delta = output_error * output * (1 - output)         # sigmoid derivative: s*(1-s)

    hidden_error = output_delta @ w2.T
    hidden_delta = hidden_error * hidden_output * (1 - hidden_output)

    #print(output_delta.shape)
    #print(hidden_delta.shape)

    learning_rate = 0.1

    w2 -= learning_rate * (hidden_output.T @ output_delta)
    b2 -= learning_rate * output_delta.sum(axis = 0)

    w1 -= learning_rate * (X.T @ hidden_delta)
    b1 -= learning_rate * hidden_delta.sum(axis = 0)

    if epoch % 1000 == 0 :
        print(f"epoch {epoch}, loss {loss}")

print(output)

