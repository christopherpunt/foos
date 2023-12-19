import neopixel, time
from machine import Pin, ADC
from time import sleep

numLeds = 3 
ledGPIO = 4 
np = neopixel.NeoPixel(machine.Pin(ledGPIO), numLeds)

def resetLights():
    np[0] = (255, 255, 255)
    np[1] = (255, 255, 255)
    np[2] = (255, 255, 255)
    np.write()

resetLights()

print( "here")

analogIn = ADC(0)
averageValue = 0


def calculateAverage():
    sumAverageValue = 0
    global averageValue
    for x in range(20):
        sumAverageValue = sumAverageValue + analogIn.read()
        sleep(0.001)
    averageValue = sumAverageValue / 20
    print(f'average: {averageValue}')
    
def isGoal(currentValue, averageValue):
    return averageValue - currentValue > 10

def Goal(currentValue):
    print(currentValue)
    print('Goal!!!')
    cycleGoalLights()
    calculateAverage()
    
def cycleGoalLights():
    #cycle for goals
    for i in range(20 * numLeds):
        for j in range(numLeds):
            np[j] = (0, 0, 0)
        np[i % numLeds] = (255, 255, 255)
        np.write()
        time.sleep_ms(50)
        resetLights() 
    
calculateAverage()
while True:
    currentValue = analogIn.read()
    sleep(0.001)
    
    if isGoal(currentValue, averageValue):
        Goal(currentValue)

  

