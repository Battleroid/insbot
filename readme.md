# insbot

Bug people in the videogames channel that people are playing Insurgency right now.

You'll need to make the following patch to python-valve for it to actually work under Python 3:

```
diff --git a/valve/rcon.py b/valve/rcon.py
index 33640b8..9db70c4 100644
--- a/valve/rcon.py
+++ b/valve/rcon.py
@@ -87,7 +87,7 @@ class RCONMessageError(RCONError):
 class RCONMessage(object):
     """Represents a RCON request or response."""

-    ENCODING = "ascii"
+    ENCODING = "utf-8"

     class Type(enum.IntEnum):
         """Message types corresponding to ``SERVERDATA_`` constants."""
@@ -707,7 +707,7 @@ class _RCONShell(cmd.Cmd):
         :param address: same as :class:`RCON`.
         :param password: same as :class:`RCON`.
         """
-        self.disconnect()
+        self._disconnect()
         self._rcon = RCON(address, password)
         try:
             self._rcon.connect()
@@ -749,7 +749,7 @@ class _RCONShell(cmd.Cmd):
                 response = self._rcon.execute(command).text
             except RCONCommunicationError:
                 print("Lost connection to server.")
-                self.disconnect()
+                self._disconnect()
             else:
                 if response.endswith("\n"):
                     response = response[:-1]
```
