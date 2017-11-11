#include<iostream>
#include<fstream>
using namespace std;
int w[13][13];
int lx[13]={0},ly[13]={0},linky[13];
bool visx[13],visy[13];
int lack;
bool find(int x,int n){
    visx[x]=true;
    for(int i=0;i<n;i++){
      if(visy[i])continue;
      int t=lx[x]+ly[i]-w[x][i];
      if(t==0){
         visy[i]=true;
         if(linky[i]==-1||find(linky[i],n)){
            linky[i]=x;
            return true;
         }
      } 
      else if(lack>t)lack=t;
   }    
   return false;
}          
int main(){

    int n;
    cin>>n;
    for(int i=0;i<n;i++)
       for(int j=0;j<n;j++)
           cin>>w[i][j];
    for(int i=0;i<n;i++)
       for(int j=0;j<n;j++)
           if(w[i][j]>lx[i])
             lx[i]=w[i][j];
  //  for(int i=0;i<n;i++)    
  //      cout<<lx[i]<<endl;     
    for(int i=0;i<n;i++)
        linky[i]=-1;
        
    for(int i=0;i<n;i++){
       for(;;){
          memset(visx,0,13);
          memset(visy,0,13); 
          lack=200000;
          if(find(i,n))break;
         // cout<<"wolf"<<' ';
       for(int j=0;j<n;j++){
          if(visx[j])lx[j]-=lack;
          if(visy[j])ly[j]+=lack;
       }
       }
   }
   int sum=0; 
   for(int i=0;i<n;i++)
      sum+=w[linky[i]][i];
   cout<<sum;                         
    char ch;
    cin>>ch;
    return 0;
} 