import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.ReflectPermission;
import java.security.Permission;
import java.util.ArrayList;

import sun.misc.Unsafe;

public class Main {
  // public static byte[] lmao;

  public static void main(String[] args) throws NoSuchMethodException,
    SecurityException,
    IllegalAccessException,
    IllegalArgumentException,
    InvocationTargetException,
    ClassNotFoundException,
    InstantiationException {

    // BufferedInputStream probablynotallowed =
    //   new BufferedInputStream(new FileInputStream(new File("FlagClient.class")));
    // ArrayList<Byte> file = new ArrayList<>();
    // int b = probablynotallowed.read();
    // while (b != -1) {
    //   file.add((byte)b);
    //   b = probablynotallowed.read();
    // }
    // Main.lmao = new byte[file.size()];
    // for (int i = 0; i < file.size(); ++i) {
    //   Main.lmao[i] = file.get(i);
    // }

    // Field f = Unsafe.class.getDeclaredField("theUnsafe");
    // f.setAccessible(true);
    // Unsafe u = (Unsafe) f.get(null);



    // ClassLoader cl = ClassLoader.getSystemClassLoader();

    // Method[] ms = cl.getClass().getDeclaredMethods();
    // for (Method m : ms) {
    //   System.out.println(m.getName());
    // }


    // Method m = cl.getClass().getDeclaredMethod("findClass", new Class[]{String.class});
    // m.setAccessible(true);
    // m.invoke(cl, "FlagClient");
    // System.out.println("success");

    System.setSecurityManager(new SecurityManager() {
      @Override
      public void checkExit(int status) {
        throw new SecurityException();
      }

      @Override
      public void checkPermission(Permission perm) {
        if (perm instanceof RuntimePermission) {
          if (perm.getName().startsWith("exitVM")) {
            throw new SecurityException();
          }
        }
        return;
      }
    });

    Class<?> c = ClassLoader.getSystemClassLoader().loadClass("FlagClient");
    // FlagClient o = new FlagClient();
    Object o = c.newInstance();
    // Class<?> c = u.defineClass("lmao", Main.lmao, 0, Main.lmao.length, null, null);
    // Class<?> c = u.defineAnonymousClass(Main.class, Main.lmao, null);

    // Object o = c.newInstance();
    Method flag = o.getClass().getDeclaredMethod("flag");
    flag.setAccessible(true);
    flag.invoke(o);
  }
}
