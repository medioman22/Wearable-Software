import mraa

print (mraa.getVersion())
x = mraa.Gpio(13)
x.dir(mraa.DIR_OUT)
x.write(1)
