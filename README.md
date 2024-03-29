# Лабораторная работа №3. Эксперимент

- Чжоу Хунсян, P33131
- `lisp -> asm | cisc -> risc | harv | hw | instr | struct | stream | port | pstr | prob5 | 8bit`
- С усложнения

## Язык программирования

### Описание синтаксиса. 

**Форма бэкуса-Наура:**

```ebnf
<program> ::= [<section_data>] <section_text>
<section_data> ::= "section .data" <data>*
<data> ::= <comment> | <variable>
<variable> ::= <name> ":" <value>
<name> ::= <character>+
<value> ::= <number> | "<string>"

<section_text> ::= "section .text" <code>*
<code> ::= <comment> | <label> | <instruction>
<label> ::= "." <name> ":"
<instruction> ::= <0arg_command> | <1arg_command> <operand> | <2arg_command> <operand> <operand>
<operand> ::= <number> | <register> 
<comment> ::= ";" <character>*

<0arg_command> ::= "HLT"
<1arg_command> ::= "INC" | "DEC" | "JMP" | "JZ" | "JE" | "JNE" | "JG" | "JGE" | "JL" | "JLE"
<2arg_command> ::= "MOV" | "ADD" | "SUB" | "MUL" | "DIV" | "MOD" | "XOR" | "CMP" 
<register> ::= "R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"
<character> ::= [a-z, A_Z, _]+
<number> ::= [0-9]+
```

- Описание семантики. В первую очередь:

  - стратегия вычислений, 
  - области видимости, 
  - типизация, виды литералов.

- Данного описания должно быть достаточно для выполнения программы "на листе бумаги".

## Организация памяти
Данный раздел является сквозным по отношению к работе и должен включать:

- модель памяти процессора, размеры машинного слова, варианты адресации;
- механику отображения программы и данных на процессор.

Модель памяти должна включать:

- Какие виды памяти и регистров доступны программисту?
- Где хранятся инструкции, процедуры и прерывания?
- Где хранятся статические и динамические данные?

```text
       Registers
+------------------------------+
| acc                          |
+------------------------------+

       Instruction memory
+------------------------------+
| 00  : jmp N                  |
|    ...                       |
| 10  : interruption vector 0  |
| 11  : interruption vector 1  |
|    ...                       |
| n   : program start          |
|    ...                       |
| i   : interruption handler 0 |
| i+1 : interruption handler 0 |
|    ...                       |
+------------------------------+

          Data memory
+------------------------------+
| 00  : constant 1             |
| 01  : constant 2             |
|    ...                       |
| l+0 : num literals           |
| l+1 : num literals           |
|    ...                       |
| c+0 : variable 1             |
|    ...                       |
+------------------------------+
```

А также данный раздел должен включать в себя описание того, как происходит работа с 1) литералами, 2) константами, 3) переменными, 4) инструкциями, 5) процедурами, 6) прерываниями во время компиляции и исполнения. К примеру:

- В каких случаях литерал будет использован при помощи непосредственной адресации?
- В каких случаях литерал будет сохранён в статическую память?
- Как будут размещены литералы, сохранённые в статическую память, друг относительно друга?
- Как будет размещаться в память литерал, требующий для хранения несколько машинных слов?
- В каких случаях переменная будет отображена на регистр?
- Как будет разрешаться ситуация, если регистров недостаточно для отображения всех переменных?
- В каких случаях переменная будет отображена на статическую память?
- В каких случаях переменная будет отображена на стек?
- И так далее по каждому из пунктов в зависимости от варианта...

Система команд

Раздел должен включать:

- Особенности процессора (всё необходимое для понимания системы команд):
    - типы данных и машинных слов;
    - устройство памяти и регистров, адресации;
    - устройство ввода-вывода;
    - поток управления и системы прерываний;
    - и т.п.
- Набор инструкций.
- Способ кодирования инструкций:
    - по умолчанию можно использовать современные структуры данных;
    - требование бинарного кодирования -- особенность конкретного варианта.
- Описания системы команд должно быть достаточно для её классификации (CISC, RISC, Acc, Stack).

Транслятор

Раздел подразумевает разработку консольного приложения:

- *Входные данные*:
    - Имя файла с исходным кодом в текстовом виде.
    - Имя файла для сохранения полученного машинного кода.
    - Другие аргументы командной строки (ключи, настройки, и т.п.).
- *Выходные данные*:
    - Имя выходного файла для машинного кода.

Раздел должен включать описание:

- Интерфейса командной строки.
- Принципов работы разработанного транслятора (этапы, правила и т.п.).

Модель процессора

Раздел подразумевает разработку консольного приложения:

- *Входные данные*:
    - Имя файла для чтения машинного кода.
    - Имя файла с данными для имитации ввода в процессор.
- *Выходные данные*:
    - Вывод данных из процессора.
    - Журнал состояний процессора, включающий:
        - состояния регистров процессора;
        - выполняемые инструкции (возможно, микрокод) и соответствующие им исходные коды;
        - ввод/вывод из процессора.

Раздел должен включать:

- Схемы DataPath и ControlUnit, описание сигналов и флагов:
    - В случае, если схемы DataPath и ControlUnit совмещены, должна быть убедительная аргументация в тексте отчёта.
    - Не стоит полностью отрисовывать сигнальные линии от ControlUnit ко всем элементам схемы, это загромождает схему и усложняет её чтение. Обозначьте их как сделано в примере.
    - Если вы настаиваете на полной отрисовке сигнальных линий, то они должны визуально отличаться от линий передачи данных / адресов.
    - Схемы должны помещаться на экран.
    - В случае, если схемы не соответствуют данным требованиям, они могут быть признаны нечитаемыми, следовательно, непроверяемыми. Пример нечитаемой схемы: [link](./fig/lab3-bad-processor-scheme.png)
- Особенности реализации процесса моделирования.

Обратите внимание, что схемы должны отражать аппаратную структуру процессора и его элементов. Делайте схемы читаемыми. На структурных элементах отображайте порты (если у вас две стрелки в регистр -- это ошибка), не забывайте мультиплексоры.

Рекомендации по реализации:

- строгое разделение DataPath и ControlUnit на уровне кода/интерфейсов/схем;
- реализация машинной арифметики на уровне схем не требуется, просто складывайте, вычитайте, умножайте и делите так, как будто это поддержано АЛУ за один такт;
- при моделировании процессов ориентироваться на схему процессора и её функционирование (а не писать отвлечённый код).

Тестирование

Раздел должен включать:

- Краткое описание разработанных тестов.
- Описание работы настроенного CI.
- Реализацию следующих алгоритмов (должны проверяться в рамках интеграционных тестов):

    1. `hello` -- напечатать hello world;

    1. `cat` -- печатать данные, поданные на вход симулятору через файл ввода (размер ввода потенциально бесконечен);

    1. `hello_user_name` -- запросить у пользователя его имя, считать его, вывести на экран приветствие (`<` -- ввод пользователя через файл ввода, `>` вывод симулятора):

        ```text
        > What is your name?
        < Alice
        > Hello, Alice!
        ```

    1. алгоритм согласно варианту;

    1. дополнительные алгоритмы, демонстрирующие особенности вашего варианта (синтаксис, работу специфических команд и т.п.).

- Необходимо показать работу разработанных алгоритмов.
    - Для одной из программ сделать подробное описание с комментариями в рамках отчёта, включая: использование разработанных программ, исходный код, машинный код, результат работы и журнал состояний модели процессора.
    - Для всех алгоритмов необходимо привести ссылки на их golden тесты. Они должны включать: алгоритм, машинный код и данные, ввод/вывод, журнал работы процессора.
    - Если размер журнала модели процессора слишком большой (сотни килобайт), его полное включение в golden test нецелесообразно. Необходимо адаптировать журнал под каждый алгоритм, добившись достаточной репрезентативности для проверки задания.
    - Все листинги исходного кода должны быть отформатированы.

Кроме того, в конце отчёта необходимо привести следующий текст для трёх реализованных алгоритмов (необходимо для сбора общей аналитики по проекту):

```text
| ФИО | <алг> | <LoC> | <code байт> | <code инстр.> | <инстр.> | <такт.> | <вариант> |
```

где:

- алг. -- название алгоритма (hello, cat, или как в варианте)
- прог. LoC -- кол-во строк кода в реализации алгоритма
- code байт -- кол-во байт в машинном коде (если бинарное представление)
- code инстр. -- кол-во инструкций в машинном коде
- инстр. -- кол-во инструкций, выполненных при работе алгоритма
- такт. -- кол-во тактов, которое заняла работа алгоритма