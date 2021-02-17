import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.security.Permission;

public class Solve {
  public static void main(String[] args) throws NoSuchMethodException,
    SecurityException,
    IllegalAccessException,
    IllegalArgumentException,
    InvocationTargetException,
    ClassNotFoundException,
    InstantiationException {

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
    Object o = c.newInstance();
    Method flag = o.getClass().getDeclaredMethod("flag");
    flag.setAccessible(true);
    flag.invoke(o);
  }
}
