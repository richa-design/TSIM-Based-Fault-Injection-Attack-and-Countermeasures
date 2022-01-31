# Makefile script with commands to generate the Fault Injection Countermeasures binaries and disassemblies.
# Description:
# all: produce elf and disassembly files for source code w/ and w/o countermeasure 
# clean: clean generated files


PREFIX     ?= sparc-gaisler-elf
CC          = $(PREFIX)-gcc
OBJDUMP     = $(PREFIX)-objdump
DEST        = elf

all: test1.c test1_checksum.c
	mkdir -p $(DEST)
	$(CC) -g test1.c -o $(DEST)/test1.elf
	$(CC) -g test1_checksum.c -o $(DEST)/test1_checksum.elf
	$(OBJDUMP) -d $(DEST)/test1.elf > $(DEST)/test1.dis
	$(OBJDUMP) -d $(DEST)/test1_checksum.elf > $(DEST)/test1_checksum.dis
	
clean:
	rm -rf elf/
