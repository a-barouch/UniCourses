// Put your code here.

(START)
	// outer = 0
	@outer 
	M=0
	
(OUTER_LOOP)
	// if (outer == r15) goto end
	@outer
	D=M
	@R15
	D=D-M
	@END
	D;JEQ
	
	// inner = r15
	@R15
	D=M
	@inner
	M=D
	// inner--
	M=M-1
	
(INNER_LOOP)
	//if (inner == outer) goto end_of_inner
	@inner
	D=M
	@outer
	D=D-M
	@END_OF_INNER
	D;JEQ
	
	// first = r14 + inner - 1
	@R14
	D=M
	@inner
	D=D+M
	@first
	M=D-1
	// second = r14 + inner
	@second
	M=D
	
	// if (*first > *second) goto skip_swap
	@first
	A=M
	D=M
	@second
	A=M
	D=D-M
	@SKIP_SWAP
	D;JGT
	
	// temp = *first
	@first
	A=M
	D=M
	@temp
	M=D
	// *first = *second
	@second
	A=M
	D=M
	@first
	A=M
	M=D
	// *second = temp
	@temp
	D=M
	@second
	A=M
	M=D
	
(SKIP_SWAP)
	// inner--
	@inner
	M=M-1
	
	// goto inner_loop
	@INNER_LOOP
	0;JMP

(END_OF_INNER)
	// outer++
	@outer
	M=M+1
	
	// goto outer_loop
	@OUTER_LOOP
	0;JMP

(END)
	@END