main : main.o demod.o complexLib.o detecteur.o
	gcc -o main main.o complexLib.o demod.o detecteur.o

main.o : main.c
	gcc -c main.c

complex.o : complexLib.h complexLib.c
	gcc -c complexLib.c

demod.o : demod.h demod.c
	gcc -c demod.c

detecteur.o : detecteur.c detecteur.h
	gcc -c detecteur.c

clear:
	rm -rf *.o main