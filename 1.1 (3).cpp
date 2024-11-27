#include<iostream>
using namespace std;
int main(){
    int q;
    cin>>q;
    while(q--){
        int n;
        cin>>n;
        char a[n][4];
        for(int i=0;i<n;i++){
            for(int j=0;j<4;j++){
                cin>>a[i][j];
            }
        }
        for(int p=n-1;p>=0;p--){
            for(int q=0;q<4;q++){
                if(a[p][q]=='#'){
                    cout<<q+1;
                    break;
                }
            }

        }
        cout<<endl;
        
       

    }
    return 0;

}