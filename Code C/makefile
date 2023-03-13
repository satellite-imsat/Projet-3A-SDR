main : main.o demod.o complexLib.o signalCaracteristics.o aisDecode.o bitTreatment.o
	gcc -o main main.o demod.o complexLib.o signalCaracteristics.o aisDecode.o bitTreatment.o -lm

main.o : main.c 
	gcc -c main.c

complexLib.o : complexLib.h complexLib.c
	gcc -c complexLib.c

demod.o : demod.h demod.c 
	gcc -c demod.c

signalCaracteristics.o : signalCaracteristics.h signalCaracteristics.c
	gcc -c signalCaracteristics.c

complexFifo.o : complexFifo.h complexFifo.c
	gcc -c complexFifo.c

bitTreatment.o : bitTreatment.h bitTreatment.c
	gcc -c bitTreatment.c

aisDecode.o : aisDecode.h aisDecode.c
	gcc -c aisDecode.c

clear:
	rm -rf *.o main testDemod testTreatment