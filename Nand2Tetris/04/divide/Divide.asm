// Put your code here.

(START)

	@R15
	M=0
	
	@R13
	D=M
	@first
	M=D
	
	@R14
	D=M
	@second
	M=D
	
(EDGE_CASES)
	
	// check if second is bigger or equal to first
	@second
	D=M
	@first
	D=D-M
	@END_EQUAL
	D;JEQ // first == second
	@END_ILLEGAL_ARG
	D;JGT //first < second
	
	// checks if second equals 0
	@second
	D=M
	@END_ILLEGAL_ARG
	D;JEQ  // second == 0
	
(LOOP)
	@first
	D=M
	@second
	D=D-M
	@SHIFT
	D;JGE // if first is larger than second, shift second
	
	@second
	M=M>>
	
(LOOP2)
	
	// check if R14>second and then algorithm run is finished
	@second
	D=M
	@R14
	D=D-M
	@END
	D;JLT
	
	@first
	D=M
	@second
	D=D-M
	
	// if second if larger than first, add 0 to result
	@ADD_ZERO
	D;JLT
	
		
	// if second if smaller than first, add 1 to result
	@ADD_ONE
	D;JGE
	

(SHIFT)
	
	@second
	D = M<< // checks if second becomes negative
	@R15
	M=M<<
	@LOOP2
	D;JLE
	
	@second
	M=M<<
	
	@LOOP
	0;JMP

(ADD_ONE)  // adds one to R15 (result)
	@R15
	M=M<<
	M=M+1
	
	@second 
	D=M
	@first
	M=M-D //substract second from first
	
	@second
	M = M>>
	
	@LOOP2
	0;JMP
	
	

(ADD_ZERO) // adds zero to R15 (result)
	@R15
	M=M<<
	
	@second
	M=M>>
	
	@LOOP2
	0;JMP

(END_EQUAL)
	@R15
	M=1

(END_ILLEGAL_ARG)
	@R15
	M=0

(END)
	@END
