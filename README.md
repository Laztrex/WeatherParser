# TaskCompilation
Plan: a collection of different tasks for encrypting / constructing artificial languages. Later merge into one global related project
> Globally: everything here is the forerunner for the artificial language generator Ro

---
## Caesar Encryptor
Цель: Необходимо написать программу, шифрующее слово с помощью [Шифра Цезаря](https://is.gd/rcGAsp).
Программа должна принимать на вход от пользователя слово и число сдвигов. 

Example:  
- Encoding
~~~
Слово:         гитхаб  
Число сдвигов: 3  
Вывод:         ёлхшгд
~~~
~~~
main_enc.py цезарь гитхаб 3 [-m enc -a ru]
~~~
- decoding
~~~
Слово:         ёлхшгд  
Число сдвигов: 3  
Вывод:         гитхаб
~~~
~~~
main_enc.py цезарь ёлхшгд 3 -m dec [-a ru]
~~~

## Vijener Encryptor
Цель: Необходимо написать программу, шифрующее слово с помощью [Шифра Виженера](https://is.gd/WEVeME).
Программа должна принимать на вход от пользователя слово и слово-ключ.

Example:  
- Encoding
~~~
Слово:         гитхаб  
Слово-ключ:    привет  
Вывод:         тщычеу
~~~
~~~
main_enc.py виженер гитхаб привет [-m enc -a ru]
~~~
- decoding
~~~
Слово:         тщычеу  
Число сдвигов: привет  
Вывод:         гитхаб
~~~
~~~
main_enc.py виженер тщычеу привет -m dec [-a ru]
~~~