# Usage

## test
Inquery keywords (words or sentences) to bing dictionary (both English and Chinese are supported)
`python bing.py keywords`

If you invoke at the first time, you will be asked wether to creat a local cache at /home/hxd (**you should replace hxd with your own username**). Only the sencond and following invoking of this program will output translations and example sentences.

## recommend configuration 
First, you need to add alias to your terminal. Let's take zsh as an example: 
Open the user terminal configuration file `vim ~/.zshrc`, then add
```
alias dict = "python /home/hxd/bing.py"
```
store it and and reload `source ~/.zshrc`. Then you can inquery keywords at any directory with
```
dict keywords
```

For convenience, you can go to [this github page](https://github.com/first20hours/google-10000-english) and run 300000 English words to store them in your local cache.