import numpy as np
import matplotlib.pyplot as plt


# Draw curves
train_perf = np.loadtxt(open("train_perf.csv", "rb"), delimiter=",", skiprows=0)
test_perf = np.loadtxt(open("test_perf.csv", "rb"), delimiter=",", skiprows=0)
# Winnings
plt.plot(test_perf[:,0], test_perf[:,1], label="Winning rate (over 50 battles)")
plt.plot(test_perf[:,0], np.ones_like(test_perf[:,0])*.5, color='red', ls='--')
plt.xlabel("Number of battles used for training")
plt.ylabel("Ratio of victories")
plt.ylim((0,1))
plt.title("Agent winnings vs. training")
plt.legend()
plt.savefig("winnings_training.jpg")
plt.show()
# Accuracy loss
plt.plot(train_perf[:,0], train_perf[:,1], label="Accuracy", color="blue")
plt.plot(train_perf[:,0], train_perf[:,2], label="Loss", color="green")
plt.xlabel("Number of battles used for training")
plt.ylabel("Accuracy / Loss")
plt.title("Accuracy and Loss vs. training")
plt.legend()
plt.savefig("acc_loss.jpg")
plt.show()


