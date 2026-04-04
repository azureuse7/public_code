def heman(stride: int):
    def f(x: int):
        return stride + x
    return f

sana = heman(10)

print(sana(5))
