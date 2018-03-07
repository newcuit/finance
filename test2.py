from stocks_net import tickInterface
ti = tickInterface()

dayi=0
days=5
while True:
    volumeIn,volumeOut,amountIn,amountOut = ti.getAmountInfo('300398',dayi)
    dayi = dayi+1
    if amountIn == 0 and amountOut == 0:
        continue
    days = days-1
    print(dayi,volumeIn,volumeOut,amountIn,amountOut)
    if days == 0:
        break
