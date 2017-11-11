#include<iostream>
using namespace std; 
int main(){
   int a[6],c[6];    
   c[0]=1;c[1]=2;c[2]=3;c[3]=5;c[4]=10;c[5]=20;
   for(int i=0;i<6;i++)
      cin>>a[i];
   int total=0;
   for(int j=1;j<1000;j++){
       //verify whether the weight j can be weighted?
       int k=j;
       for(int i=5;i>=0;i--){
           int amount=a[i];
           if(k>=c[i] && amount>0){
               k-=c[i];
               amount--;
           }
       }
       if(k==0)
           total++;
   }       
   
   cout<<"Total="<<total;
   

   return 0;
}

