package HMM;

class Forward extends HMMMaster {

    Forward(double[] init, double[][] a, double[][] b, int[] o){
        super.init = init;
        super.a = a;
        super.b = b;
        super.o = o;
    }

    void execute() {
        for (int j = 0; j < v[0].length; j++) {
            // j resembles an iteration into each state, hot or cold.
            // init[j] resembles the initial probability of each state.
            // b[obs[0] - 1][j] resembles the observational likelihood of one observation in a state.
            v[0][j] = init[j] * b[j][o[0] - 1];
        }

        for (int i = 1; i < v.length; i++) {
            for (int j = 0; j < v[i].length; j++) {
                double sum = 0;
                for (int k = 0; k < states; k++) {
                    sum += v[i - 1][k] * a[k][j] * b[j][o[i] - 1];
                }
                v[i][j] = sum;
            }
        }
    }
}