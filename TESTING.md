## Running the unit tests

```
mkdir code
cd code
git clone https://github.com/vivisect/vivisect
git clone https://github.com/vivisect/vivtestfiles
cd vivisect
VIVTESTFILES=../vivtestfiles python2 -m unittest discover
```

If you want to see the code coverage stats:
```
cd vivisect
VIVTESTFILES=../vivtestfiles coverage -m unittest discover
coverage html
```
And then open vivisect/coverage\_html\_report/index.html
