#include <stdio.h> 

int main()
{
	int x, y, y_cs;
	
	x = 25;
	y = x;
	y_cs = ~x;
	
	if((y ^ y_cs) != 0xFF)
		printf("{Fault Detected}");
	else
		y = y - 10;

return 0;
}
