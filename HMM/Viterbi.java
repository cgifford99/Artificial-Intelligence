package HMM;

public class Viterbi extends HMMMaster {

    public void execute(){
        // initial calculations
        for(int j = 0; j < v[0].length; j++){
            v[0][j] = init[j] * b[j][o[0] - 1];
            bt[0][j] = 0;
        }

        // the rest
        for(int i = 1; i < v.length; i++){
            for(int j = 0; j < v[i].length; j++){
                double[] maxV = new double[states];
                // calculate probability
                for(int k = 0; k < states; k++){
                    maxV[k] = v[i-1][k] * a[k][j] * b[j][o[i] - 1];
                }
                // find maximum
                for(int k = 0; k < maxV.length; k++){
                    if(maxV[k] > v[i][j]){
                        v[i][j] = maxV[k];
                        bt[i][j] = k;
                    }
                }
            }
        }
    }
}
