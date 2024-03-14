section .data
    a:2
    b:3
    res:0
section .text
    _start:
    .loop:
        mov a, b
        HLT