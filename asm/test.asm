section .data
    a:3
    b:5

section .text
_start:
.loop:
    ld a
    add b
    st OUTPUT
    HLT