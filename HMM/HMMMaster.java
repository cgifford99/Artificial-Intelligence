package HMM;

import java.util.Arrays;

public class HMMMaster {

    String[] stateNames = {"HOT", "MILD", "COLD"};
    int states = stateNames.length;
    int[] o = new int[3];                     // the probability of this observation set will be calculated
    double[] init = new double[states];
    double[][] a = new double[states][states];
    double[][] b = new double[states][o.length];
    double[][] v = new double[o.length][states]; // overall probability calculation storage
    int[][] bt = new int[o.length][states]; // backtrace. only used in Viterbi algorithm

    public HMMMaster(){
        // Verify probability array summed to 1;
        for(int i = 0; i < a.length; i++){
            probVerifi(a[i], "a" + i);
        }

        for(int i = 0; i < b.length; i++){
            probVerifi(b[i], "b");
        }

        probVerifi(init, "init");
    }

    public static void probVerifi(double[] a, String name){
        if(Math.abs(1 - Arrays.stream(a).sum()) > 0.000001){
            System.out.printf("Probability array [%s] not summed to 1\n", name);
            System.exit(1);
        }
    }
}
