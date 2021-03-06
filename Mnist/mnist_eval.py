import time
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from Mnist.mnist_inference import*
from Mnist.mnist_train import *

# 每10秒加载一次最新的模型，并在测试数据上测试最新模型的正确率
EVAL_INTEVAL_SECS = 10

def evaluate(mnist):
    with tf.Graph().as_default() as g:
        # 定义输入输出的格式
        x = tf.placeholder(dtype=tf.float32,shape=[None,INPUT_NODE],name="x-input")
        y_ = tf.placeholder(dtype=tf.float32,shape=[None,OUTPUT_NODE],name="y-input")
        validate_feed={
            x:mnist.validation.images,
            y_:mnist.validation.labels
        }
        # 直接调用封装好的函数计算前向传播结果，因为测试时不关注正则化损失的值，所以这里用于计算正则化损失的值被设置为None
        y = inference(x,None)
        correct_prediction = tf.equal(tf.argmax(y_,1),tf.argmax(y,1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction,tf.float32))

        # 通过变量重命名的方式来加载模型，这样在前向传播的过程中就不需要调用求滑动平均的函数来获取平均值了。
        variable_average=tf.train.ExponentialMovingAverage(MOVING_AVERAGE_DECAY)
        variables_to_restore = variable_average.variables_to_restore()
        saver = tf.train.Saver(variables_to_restore)

        # 每隔10秒调用一次计算正确率的过程以检测训练过程中正确率的变化
        while True:
            with tf.Session() as sess:
                # tf.train.get_chechpoint_state函数会通过checkpoint文件自动找到目录中最新模型的文件名
                ckpt = tf.train.get_checkpoint_state(MODEL_SAVE_PATH)
                if ckpt and ckpt.model_checkpoint_path:
                    # 加载模型
                    saver.restore(sess,ckpt.model_checkpoint_path)
                    # 通过文件名得到模型保存时迭代的轮数
                    global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
                    accuracy_score = sess.run(accuracy,feed_dict=validate_feed)
                    print("After %s training steps,validation accuracy = %g"%(global_step,accuracy_score))
                else:
                    print("No checkpoint file found")
                    return
                time.sleep(EVAL_INTEVAL_SECS)
def main(argv=None):
    mnist = input_data.read_data_sets("E:/learn/Master/tensorflow/MNIST_data/", one_hot=True)
    evaluate(mnist)
if __name__=="__main__":
    tf.app.run()
