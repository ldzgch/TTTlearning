import tensorflow.keras as tfk
import numpy as np

def simpleFF(layerunits=[50,100,10],insize=10,tfk_activation=tfk.activations.relu,bias=True): # simple feedforward network
    tmp = tfk.models.Sequential()
    if layerunits:
        tmp.add(tfk.layers.Dense(layerunits[0],activation=tfk_activation,input_shape=(insize,),use_bias=bias))
    else:
        return None
    for Units in layerunits[1:]:
        tmp.add(tfk.layers.Dense(Units,activation=tfk_activation,use_bias=bias))

    tmp.compile(
        optimizer=tfk.optimizers.SGD(0.3),
        loss='mse')

    return tmp




def ConvNet(filterunits=[[5,5,10],[3,3,20],[5,5,16]],insize=(10,10,3),tfk_activation=tfk.activations.relu,bias=True):
    tmp = tfk.models.Sequential()
    if filterunits:
        tmp.add(tfk.layers.Conv2D(filterunits[0][2],filterunits[0][:2],activation=tfk_activation,input_shape=insize,use_bias=bias,padding='same'))
    else:
        return None
    for Units in filterunits[1:]:
        tmp.add(tfk.layers.Conv2D(Units[2],Units[:2],activation=tfk_activation,use_bias=bias,padding='same'))

    tmp.compile(
        optimizer=tfk.optimizers.SGD(0.3),
        loss='mse')

    return tmp


if __name__ == '__main__':
##    
##    sff = simpleFF([2,2],3,bias=False)
##    print(sff.variables)

    cn = ConvNet([[3,3,3]],(5,5,3))
    print(cn.predict(np.random.random((1,5,5,3))))
