package HMM;

import java.util.Arrays;

public class HMMClient extends HMMMaster{

    public static void main(String[] args){
        // Start probability calculations for all possible observation sequences
        String[] stateNames = {"HOT", "MILD", "COLD"};
        double[] init = {0.3, 0.3, 0.4};                         // initial probabilities (HOT, COLD)
        double[][] a = {{0.4, 0.4, 0.2}, {0.3, 0.4, 0.3}, {0.4, 0.4, 0.2}};            // transition probabilities (from state(i) to state(j), (HOT, COLD))
        double[][] b = {{0.2, 0.4, 0.4}, {0.5, 0.4, 0.1}, {0.4, 0.4, 0.2}};  // observational likelihoods (hidden states | observational states, (HOT, COLD))
        int[] o = new int[]{1, 1, 1};

        for(int i = 1; i <= o.length; i++){
            for(int j = 1; j <= o.length; j++){
                for(int k = 1; k <= o.length; k++){
                    Forward ff = new Forward(init, a, b, o); // takes in set a, b and o

                    // calculate compounded probabilities for all other observation layers
                    ff.execute();

                    // System.out.println(Arrays.deepToString(ff.v));
                    double finalProb = 0.0;
                    for(int l = 0; l < ff.v.length; l++){
                        finalProb += Arrays.stream(ff.v[l]).sum();
                    }
                    System.out.println(Arrays.toString(ff.o) + " " + finalProb);
                }
            }
        }
        System.out.println();

        Viterbi vb = new Viterbi();


        for(int i = 1; i <= vb.o.length; i++) {
            for (int j = 1; j <= vb.o.length; j++) {
                for (int k = 1; k <= vb.o.length; k++) {
                    vb.o = new int[]{i, j, k};

                    vb.execute();

                    double[] maxV = new double[vb.v.length];
                    String[] maxBT = new String[vb.v.length];
                    for(int m = 0; m < vb.v.length; m++){
                        for(int n = 0; n < vb.v[m].length; n++){
                            if(maxV[m] < vb.v[m][n]){
                                maxV[m] = vb.v[m][n];
                                maxBT[m] = stateNames[n];
                            }
                        }
                    }

                    System.out.println(Arrays.toString(vb.o) + Arrays.toString(maxBT));
                    vb.v = new double[vb.o.length][vb.states];
                    vb.bt = new int[vb.o.length][vb.states];
                }
            }
        }
    }
}
