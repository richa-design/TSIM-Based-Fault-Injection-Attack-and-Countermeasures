#include <stdio.h>

int main()
{
	int i, y, n;
	
	y = 0;
	n = 20;
	
	for(i = 0; i < n; i++)
		y = y + 1;
	
	if(i != n)
		printf("{Fault Detected}");
	
return 0;
}
