main : main.o demod.o complexLib.o
	gcc -o main main.o complexLib.o demod.o

main.o : main.c
	gcc -c main.c

complex.o : complexLib.h complexLib.c
	gcc -c complexLib.c

demod.o : demod.h demod.c
	gcc -c demod.c

clear:
	rm -rf *.o main