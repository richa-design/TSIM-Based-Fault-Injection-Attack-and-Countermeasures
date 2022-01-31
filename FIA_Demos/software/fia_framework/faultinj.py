import sys, os
import subprocess, pty, select, time
import re, random
import matplotlib.pyplot as plt



class Tsim():

    def __init__(self, progname):
        self.progname = progname
        self.q = select.poll()
        self.load_tsim()
        self.done = False
        self.lpc = 0
        self.output_regex = re.compile('{(.*?)}',flags=re.DOTALL)
        self.control_faults = 0
        self.data_faults = 0


    def load_tsim(self,):

        master, slave = pty.openpty()
        self.master = master
        self.slave = slave
        
        abs_path = os.path.abspath("../")
        self.path = abs_path + "/software/tsim-eval/tsim/linux-x64/tsim-leon3"
	
        self.tsim = subprocess.Popen([self.path, self.progname], stdin=slave, stdout=slave, close_fds=True)

        self.stdout = os.fdopen(self.master)
        self.q.register(self.stdout, select.POLLIN)
        time.sleep(2)
        self.read(23)



    def kill(self,):
        self.tsim.kill()
        os.close(self.slave)


    def read(self,lines):
        s = []
        l = self.q.poll(1)
        if not l:
            l = self.q.poll(2)
            if not l:
                l = self.q.poll(3)
                if not l:
                    l = self.q.poll(4)
                    if not l:
                        return None


        for i in range(0,lines):
            l = self.stdout.readline()
            while l[0] == '#':
                l = self.stdout.readline()
            s.append(l)


        return s

    def write(self, s):
        b = s.encode()
        n = os.write(self.master, b)
        time.sleep(2)


    def refresh_regs(self):
        self.write('reg\n')
        # read next 15 lines for register file
        rf = None
        i =0
        while rf is None:
            rf=self.read(16)
            i += 1
            if i > 5:
                raise IOError('register file is none')

        if 'LOCALS' in rf[1]:
            rf = rf[1:]
        regs = rf[1:1+8]
        special = rf[10]

        self.iregs = []
        self.lregs = []
        self.oregs = []
        self.gregs = []
        self.sregs = []

        for i in regs:
            self.iregs.append(int(i[9:9+8],16))  # store hex value as decimal value
            self.lregs.append(int(i[17+3:20+8],16))
            self.oregs.append(int(i[28+3:31+8],16))
            self.gregs.append(int(i[39+3:42+8],16))

        self.sregs.append(int(special[8:8+8],16))
        self.sregs.append(int(special[16+8:24+8],16))
        self.sregs.append(int(special[32+8:40+8],16))
        self.sregs.append(int(special[48+6:54+8],16))

        self.pc = int(rf[12][9:9+8],16)
        self.npc = int(rf[13][9:9+8],16)
        self.pc_instr = rf[12][19:rf[12].find(" ", 19)]
        self.npc_instr = rf[13][19:rf[13].find(" ", 19)]


    def read_reg(self, reg):
        c = reg[0]
        if c == 'i':
            return self.iregs[int(reg[1])]
        if c == 'l':
            return self.lregs[int(reg[1])]
        if c == 'o':
            return self.oregs[int(reg[1])]
        if c == 'g':
            return self.gregs[int(reg[1])]

        if reg == 'psr':
            return self.sregs[0]
        if reg == 'wim':
            return self.sregs[1]
        if reg == 'tbr':
            return self.sregs[2]
        if reg == 'y':
            return self.sregs[3]

        if reg == 'pc':
            return self.pc
        if reg == 'npc':
            return self.npc

        raise ValueError('invalid register: ',reg)

    def write_reg(self, reg, val):
        c = reg[0]
        if c not in 'ilog':
            if reg not in ['psr','wim','tbr','y', 'pc','npc']:
                raise ValueError('invalid register: '+reg)

        self.write('reg '+reg+' '+str(val)+'\n')
        l = self.read(2)


    def write_mem(self, addr, val):
        self.write('wmem '+'0x'+addr+' '+str(hex(val))+'\n')
        l = self.read(1)
        rval = self.read_mem(addr)
        if rval != val:
            print("Write to memory is incorrect")


    def read_mem(self, addr):
        self.write('mem '+'0x'+addr+' '+'4'+'\n')
        l = self.read(2)[1]
        val = int(l[14:14+8], 16)
        return val



    def run_until(self, func_or_addr):
        func_or_addr = str(func_or_addr)
        self.write('bp '+func_or_addr+'\n')

        l = self.read(2)[1]

        bp_num = int(l[13:l.index('at')-1])
        self.write('run\n')
        l = self.read(4)
        self.write('bp delete '+str(bp_num)+'\n')
        self.read(1)
        self.step()


    def step(self,):
        self.write('step\n')
        l = self.read(2)

        if l is None:
            return '','',''

        while True:
            try:
                l = l[1]
                addr = int(l[9:17],16)
                if 'nop' not in l:
                    instr = l[29:l.find(" ", 29)]
                    args = l[29+10:l.rfind(" ", 29+10, len(l)-30)].strip()
                else:
                    instr = 'nop'
                    args = ''

                self.lpc = addr

                return addr, instr, args
            except:
                if ' Program exited normally on CPU 0.\n' in l:
                    sys.stderr.write('Program finished')
                    self.done = True
                else:
                    print('unknown string: '+l)



    def cont(self,):
        self.write('cont\n')
        l = self.read(1)

    def dis(self,):
        self.write('disassemble\n') # disassemble one instruction
        l = self.read(20)
        return l

    def check_output(self,):
        out = ''

        i = 0
        self.write('reset\n')
        self.write('bt\n')
        l = self.read(3)

        if l is not None:
            for i in range(len(l)):
                out += l[i]

        while ' Program exited normally on CPU 0.\n' not in out:
            i += 1
            if 'CPU 0 in error mode' in out:
                self.match = 'IU in error mode'
                return 3
            elif i > 1000:
                raise IOError('read returning None')
            else:
                # this is a hack
                self.write('reset\n')
                self.write('bt\n')

                l = self.read(1)
                if l:
                    out += l[0]


        match = ''
        try:
            match = self.output_regex.search(out).group(1)
        except AttributeError:
            self.match = '(no output)'
            return 2

        if 'DATA' in match:
            self.match = '(no output)'
            self.data_faults += 1
            return 2
        elif 'CONTROL' in match:
            self.control_faults += 1
            self.match = '(no output)'
            return 2


        self.match = match
        if match == self.correct_output:
            return 0
        return 1

    def get_registers(self,s):
        regs = []
        num = s.count('%')
        for _ in range(0,num):
            i = s.index('%')
            if s[i+1] in 'gilo':
                regs.append(s[i+1:i+3])
                s = s[i+3:]
            elif s[i+1:i+3] in ['fp','sp']:
                # frame pointer is i6
                regs.append('i6')
                s = s[i+3:]
            elif s[i+1:i+4] in ['psr','wim','tbr']:
                regs.append(s[i+1:i+4])
                s = s[i+4:]
            elif s[i+1:i+3] == 'hi':
                pass
            else:
                print(hex(self.pc))
                print(hex(self.npc))
                raise ValueError('invalid register: ' + s)

        return regs




    def reset(self,):
        self.kill()
        self.load_tsim()
        self.lpc = 0


    def resolve_label(self, label):
        try:
            return int(label)
        except:
            self.write('break '+label + '\n')
            l = self.read(1)[0]
            #print l
            #l = self.read(2)[1]
            self.log(l)
            #print l
            bp_num = int(l[10:l.index('at')-1])
            addr = int(l[l.index(':')-8:l.index(':')],16)
            self.write('del '+str(bp_num)+'\n')
            #print addr
            return addr


class FaultInjector(Tsim):
    def __init__(self,progname, **kwargs):
        Tsim.__init__(self,progname)
        self.start = 'main'
        self.end = 0x400012d4
        self.correct_output = ''

        self.num_faults = kwargs.get('num_faults',1)
        self.num_bits = kwargs.get('num_bits',1)
        self.num_skips = kwargs.get('num_skips',0) # instruction skip
        self.data_error = kwargs.get('data_error',0) # random single/multiple bit error
        self.instr_modify = kwargs.get('instr_modify',0) # instruction modify
        self.verbose = kwargs.get('verbose',False)
        self.consecutive_bits = kwargs.get('consecutive_bits',1)
        self.rbyte = kwargs.get('byte',False) #random byte error

        self.report = []
        self.coverage = 0
        self.num_faulty = 0
        self.num_correct = 0
        self.iteration = 0

    def add_record(self, iteration, instr_num, output, faulty, ftype, addr, instru, reg_affected, origval, faultyval):
        """
            ftype:
                0: correct output
                1: incorrect output
                2: no output
                3: processor crashed
        """
        useful = 0
        if ftype == 1:
            useful = 1

        self.report.append([iteration, instr_num, output, faulty, ftype, addr, instru, reg_affected, origval, faultyval, useful])
        pass

    def produce_report(self,):
        num_crashes = 0
        num_no_output = 0
        num_incorrect_out = 0
        num_correct = 0
        for i in self.report:
            if i[4] == 3:
                num_crashes += 1
            elif i[4] == 2:
                num_no_output += 1
            elif i[4] == 1:
                num_incorrect_out += 1
            elif i[4] == 0:
                num_correct += 1

        plt.style.use('ggplot')

        x = ['Correct output', 'Incorrect output', 'No output', 'Processor crashed']
        y = [num_correct, num_incorrect_out, num_no_output, num_crashes]

        x_pos = [i for i, _ in enumerate(x)]

        plt.bar(x, y, color='green')
        plt.xlabel("classification of output")
        plt.ylabel("count")
        plt.title("classification of output over %d iterations" %(self.iteration))

        plt.xticks(x_pos, x)
        
        plt.savefig('output_plot.png')

        assert(len(self.report) == (num_crashes + num_no_output + num_incorrect_out + num_correct))
        assert(num_correct == self.num_correct)

        print("Correct Output = %d, Incorrect Output = %d, No Output = %d,  Processor crashed = %d," %(num_correct, num_incorrect_out, num_no_output, num_crashes))


    def set_range(self, func_or_addr_start, func_or_addr_end):
        self.set_start(func_or_addr_start)
        self.set_end(func_or_addr_end)

    def set_start(self, func_or_addr):
        self.start = func_or_addr

    def set_end(self, func_or_addr):
        self.end = self.resolve_label(func_or_addr)

    def set_correct_output(self,out):
        self.correct_output = out

    def get_error(self, val):
        fval = val

        bitsize = 32
        additional_shift = 0

        # Random byte fault
        if self.rbyte:
            bitsize = 8
            additional_shift = ([0,8,16,24])[random.randint(0,3)]

        if self.data_error == 0:
            for j in range(0,self.num_bits):
                ra = random.randint(0,bitsize - self.consecutive_bits)
                for i in range(0, self.consecutive_bits):
                    fval = fval ^ (1<<(ra + additional_shift))
                    ra += 1

            return fval
        else:
            return (val ^ self.data_error)


    def attack(self,):
        atEndOfRange = False
        i = 0
        while not atEndOfRange:
            regi = i
            instri = i
            regs = []
            last_regs = []
            instr = 1
            ftype = 0
            faults = self.num_faults
            self.run_until(self.start)
            self.range_count = 0
            while True:
                try:
                    last_regs = regs[:]
                    last_faults = faults
                    last_regi = regi
                    last_instr = instr
                    last_instri = instri
                    while self.lpc != self.end and faults > 0:
                        
                        self.range_count += 1
                        #(addr, opcode, args) = self.step()
                        #self.log(str(hex(addr))+" "+str(opcode) +" "+args)
                        faulted_instruction = ''
                        faulted_pc = 0

                        register_affected = -1
                        origval = 0
                        faultval = 0
                        #self.refresh_regs()

                        # put fault stuff here
                        # instruction skip
                        if self.num_skips and instr > instri and not(self.instr_modify):
                            (addr, opcode, args) = self.step()
                            self.log(str(hex(addr)) + " " + str(opcode) + " " + args)
                            self.refresh_regs()
                            pc = self.read_reg('pc')
                            npc = self.read_reg('npc')
                            for j in range(1,self.num_skips):
                                npc += 4
                            self.write_reg('pc',npc)
                            faults -= 1
                            faulted_instruction = self.pc_instr
                            faulted_pc = self.pc
                            self.log(str(hex(self.pc)) +' '+ self.pc_instr +' '+"(skipped +"+str(self.num_skips-1)+')')
                            self.log('pc: ' + str(hex(pc)) + ' -> ' + str(hex(npc)))



                        # Random Bit-Flip - single/multiple
                        if (self.num_bits and not(self.instr_modify)):
                            (addr, opcode, args) = self.step()
                            self.log(str(hex(addr)) + " " + str(opcode) + " " + args)
                            self.refresh_regs()
                            new_regs = self.get_registers(args)
                            print(new_regs)
                            regs += new_regs
                            print(regs)

                            if len(regs) > regi:
                                val = self.read_reg(regs[regi])

                                # inject a bit flip
                                fval = self.get_error(val)
                                self.write_reg(regs[regi], fval)
                                faulted_instruction = opcode+' '+args
                                faulted_pc = addr

                                self.log('%s: %s -> %s' % (regs[regi], hex(val), hex(fval)))
                                self.refresh_regs()

                                register_affected = -(len(regs)-len(new_regs) - regi)
                                origval = val
                                faultval = fval

                                regi += 1
                                faults -= 1

                        # opcode change
                        if self.instr_modify and self.num_bits:
                            l = self.dis()[3]
                            addr = l[3:3 + 8]
                            op = int(l[13:13 + 8], 16)
                            inst = l[24:l.find(" ", 24)]
                            arg = l[34:l.rfind(" ", 34, 59)].strip()

                            # inject a bit flip
                            fop = self.get_error(op)
                            self.write_mem(addr, fop)
                            l = self.dis()[3]
                            finst = l[24:l.find(" ", 24)]
                            farg = l[34:l.rfind(" ", 34, 59)].strip()
                            faulted_instruction = str(hex(op)) + ' ' + inst + ' ' + arg
                            faulted_pc = addr
                            faults -= 1

                            self.log('Opcode faulted at 0x%s: %s -> %s resulting in %s %s -> %s %s' % (
                            addr, hex(op), hex(fop), inst, arg, finst, farg))
                            (addr, opcode, args) = self.step()
                            self.log(str(hex(addr)) + " " + str(opcode) + " " + args)

                        instr += 1
                    self.cont()
                    ftype = self.check_output()
                    break
                except:
                    print("An exception occurred")
                    
                    
                    regs = last_regs[:]
                    instr = last_instr
                    regi = last_regi
                    faults = last_faults
                    instri = last_instri

           
            correct = 1
            if ftype == 0:
                self.num_correct += 1
                self.log('output is correct (%s)' % self.match)
                self.log('')
            else:
                correct = 0
                self.num_faulty += 1
                self.log('output is incorrect (%s)' % self.match)
                self.log('')
            self.add_record(self.iteration, i, self.match, correct, ftype, faulted_pc, faulted_instruction,
                            register_affected, origval, faultval)
            i += 1
            atEndOfRange = (self.lpc == self.end)

            
            self.reset()


        self.iteration += 1
        

    def log(self, s):
        if self.verbose:
            sys.stderr.write(str(s)+'\n')


def run(start, end, num_faults, num_bits, cflips, num_skips, iterations, err, instr_modify, verbose, binary, correct, byte):


    fi = FaultInjector(binary, num_faults=num_faults, num_bits=num_bits, num_skips=num_skips,
            data_error=err, instr_modify=instr_modify, verbose=verbose, consecutive_bits = cflips, byte=byte)

    fi.set_correct_output(correct)
    fi.set_range(start, end)

    for j in range(0,iterations): fi.attack()

    fi.produce_report()


    
