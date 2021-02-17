import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;

public class Main {
  public static void main(String[] args) throws Exception {

    byte[] var1 = new byte[]{110, 121, 107, 118, 103, 57, 123, 57, 82, 57, 106, 62, 99, 121, 82, 57, 122, 62, 126, 98, 96, 62, 82, 53, 60, 60, 59, 107, 57, 108, 105, 107, 52, 57, 111, 110, 112};

    for (int var2 = 0; var2 < var1.length; ++var2) {
      var1[var2] = (byte)(var1[var2] ^ 13);
    }


    String out = "flag.txt";
    BufferedOutputStream bof = new BufferedOutputStream(new FileOutputStream(new File(out)));
    // bof.write(new TIEIZ().data);
    bof.write(var1);
    bof.close();
  }
}
