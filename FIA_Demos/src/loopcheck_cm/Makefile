# Makefile script with commands to generate the Fault Injection Countermeasures binaries and disassemblies.
# Description:
# all: produce elf and disassembly files for source code w/ and w/o countermeasure 
# clean: clean generated files


PREFIX     ?= sparc-gaisler-elf
CC          = $(PREFIX)-gcc
OBJDUMP     = $(PREFIX)-objdump
DEST        = elf

all: test2.c test2_loopcheck.c
	mkdir -p $(DEST)
	$(CC) -g test2.c -o $(DEST)/test2.elf
	$(CC) -g test2_loopcheck.c -o $(DEST)/test2_loopcheck.elf
	$(OBJDUMP) -d $(DEST)/test2.elf > $(DEST)/test2.dis
	$(OBJDUMP) -d $(DEST)/test2_loopcheck.elf > $(DEST)/test2_loopcheck.dis
	
clean:
	rm -rf elf/
