@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label0
D;JEQ
@SP
A=M-1
M=0
(label0)
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label1
D;JEQ
@SP
A=M-1
M=0
(label1)
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label2
D;JEQ
@SP
A=M-1
M=0
(label2)
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@POS_Ylabel3
D;JGT
@NEG_Ylabel3
D;JLE
(POS_Ylabel3)
@SP
A=M-1
D=M
@POS_X_Ylabel3
D;JGT
@POS_Y_NEG_Xlabel3
D;JLE
(NEG_Ylabel3)
@SP
A=M-1
D=M
@NEG_Y_POS_Xlabel3
D;JGT
@NEG_X_Ylabel3
D;JLE
(POS_X_Ylabel3)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label3
D;JLT
@SP
A=M-1
M=0
(label3)
@ENDlabel3
0;JMP
(NEG_X_Ylabel3)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label3
D;JLT
@SP
A=M-1
M=0
(label3)
@ENDlabel3
0;JMP
(NEG_Y_POS_Xlabel3)
@SP
A=M-1
M=0
@ENDlabel3
0;JMP
(POS_Y_NEG_Xlabel3)
@SP
A=M-1
M=-1
@ENDlabel3
0;JMP
(ENDlabel3)
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@POS_Ylabel4
D;JGT
@NEG_Ylabel4
D;JLE
(POS_Ylabel4)
@SP
A=M-1
D=M
@POS_X_Ylabel4
D;JGT
@POS_Y_NEG_Xlabel4
D;JLE
(NEG_Ylabel4)
@SP
A=M-1
D=M
@NEG_Y_POS_Xlabel4
D;JGT
@NEG_X_Ylabel4
D;JLE
(POS_X_Ylabel4)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label4
D;JLT
@SP
A=M-1
M=0
(label4)
@ENDlabel4
0;JMP
(NEG_X_Ylabel4)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label4
D;JLT
@SP
A=M-1
M=0
(label4)
@ENDlabel4
0;JMP
(NEG_Y_POS_Xlabel4)
@SP
A=M-1
M=0
@ENDlabel4
0;JMP
(POS_Y_NEG_Xlabel4)
@SP
A=M-1
M=-1
@ENDlabel4
0;JMP
(ENDlabel4)
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@POS_Ylabel5
D;JGT
@NEG_Ylabel5
D;JLE
(POS_Ylabel5)
@SP
A=M-1
D=M
@POS_X_Ylabel5
D;JGT
@POS_Y_NEG_Xlabel5
D;JLE
(NEG_Ylabel5)
@SP
A=M-1
D=M
@NEG_Y_POS_Xlabel5
D;JGT
@NEG_X_Ylabel5
D;JLE
(POS_X_Ylabel5)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label5
D;JLT
@SP
A=M-1
M=0
(label5)
@ENDlabel5
0;JMP
(NEG_X_Ylabel5)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label5
D;JLT
@SP
A=M-1
M=0
(label5)
@ENDlabel5
0;JMP
(NEG_Y_POS_Xlabel5)
@SP
A=M-1
M=0
@ENDlabel5
0;JMP
(POS_Y_NEG_Xlabel5)
@SP
A=M-1
M=-1
@ENDlabel5
0;JMP
(ENDlabel5)
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@POS_Ylabel6
D;JGT
@NEG_Ylabel6
D;JLE
(POS_Ylabel6)
@SP
A=M-1
D=M
@POS_X_Ylabel6
D;JGT
@POS_Y_NEG_Xlabel6
D;JLE
(NEG_Ylabel6)
@SP
A=M-1
D=M
@NEG_Y_POS_Xlabel6
D;JGT
@NEG_X_Ylabel6
D;JLE
(POS_X_Ylabel6)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label6
D;JGT
@SP
A=M-1
M=0
(label6)
@ENDlabel6
0;JMP
(NEG_X_Ylabel6)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label6
D;JGT
@SP
A=M-1
M=0
(label6)
@ENDlabel6
0;JMP
(NEG_Y_POS_Xlabel6)
@SP
A=M-1
M=-1
@ENDlabel6
0;JMP
(POS_Y_NEG_Xlabel6)
@SP
A=M-1
M=0
@ENDlabel6
0;JMP
(ENDlabel6)
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@POS_Ylabel7
D;JGT
@NEG_Ylabel7
D;JLE
(POS_Ylabel7)
@SP
A=M-1
D=M
@POS_X_Ylabel7
D;JGT
@POS_Y_NEG_Xlabel7
D;JLE
(NEG_Ylabel7)
@SP
A=M-1
D=M
@NEG_Y_POS_Xlabel7
D;JGT
@NEG_X_Ylabel7
D;JLE
(POS_X_Ylabel7)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label7
D;JGT
@SP
A=M-1
M=0
(label7)
@ENDlabel7
0;JMP
(NEG_X_Ylabel7)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label7
D;JGT
@SP
A=M-1
M=0
(label7)
@ENDlabel7
0;JMP
(NEG_Y_POS_Xlabel7)
@SP
A=M-1
M=-1
@ENDlabel7
0;JMP
(POS_Y_NEG_Xlabel7)
@SP
A=M-1
M=0
@ENDlabel7
0;JMP
(ENDlabel7)
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@POS_Ylabel8
D;JGT
@NEG_Ylabel8
D;JLE
(POS_Ylabel8)
@SP
A=M-1
D=M
@POS_X_Ylabel8
D;JGT
@POS_Y_NEG_Xlabel8
D;JLE
(NEG_Ylabel8)
@SP
A=M-1
D=M
@NEG_Y_POS_Xlabel8
D;JGT
@NEG_X_Ylabel8
D;JLE
(POS_X_Ylabel8)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label8
D;JGT
@SP
A=M-1
M=0
(label8)
@ENDlabel8
0;JMP
(NEG_X_Ylabel8)
@SP
A=M
D=M
@SP
A=M-1
D=M-D
M=-1
@label8
D;JGT
@SP
A=M-1
M=0
(label8)
@ENDlabel8
0;JMP
(NEG_Y_POS_Xlabel8)
@SP
A=M-1
M=-1
@ENDlabel8
0;JMP
(POS_Y_NEG_Xlabel8)
@SP
A=M-1
M=0
@ENDlabel8
0;JMP
(ENDlabel8)
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M+D
@SP
M=M+1
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M-D
@SP
M=M+1
@SP
A=M-1
M=-M
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M&D
@SP
M=M+1
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=M|D
@SP
M=M+1
@SP
A=M-1
M=!M
