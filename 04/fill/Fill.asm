// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.







(CONTROL)

	@KBD
	D=M
	

	@WHITE_SCREEN
	D;JEQ // if a key is not pressed, whiten the board

	@BLACK_SCREEN
	0;JMP // if a key is pressed, blacken the board
	
(WHITE_SCREEN)
	@bittype
	M=0
	@COLORING
	0;JMP

(BLACK_SCREEN)
	@bittype
	M=-1
	@COLORING
	0;JMP
(COLORING)

	@SCREEN
	D=A

	@addr
	M=D //addr = screen address

	@8192
	D=A
	@n
	M=D //n = the number of pixels in the screen divided by 16

	@i
	M=0 // i = 0

(LOOP)

	// checks if i >n
	@i
	D=M
	@n
	D=D-M
	@CONTROL
	D;JEQ //if i=n goto CONTROL
	
	@bittype
	D=M
	@addr
	A=M
	M=D // 16 bits of the type - black or white

	@i
	M=M+1
	@addr
	M=M+1
	@LOOP
	0;JMP
	



