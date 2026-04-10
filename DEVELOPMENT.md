# Development

## Allow explicit relative imports

Absolute imports are brittle and a little cumbersone to write it out. The sweet spot is about one (max two) layers deep in the hierarchy, so `import foo` or `import foo.bar`. Absolute imports make sense when one package talks to another, however when you're inside a package they are not very useful. After you add some typing, you'll quickly find the first way to save space is to loosen your adherence to absolute imports.

Why not try out explicit relative imports like this:

```
from . import foo, bar
```

```
from .foo import baz
```

```
from .. import foo
```

They're easier to work with as they make it clear you're importing from within the same package.

However, if you add explicit relative imports and run these scripts from the command line you'll get an error like this:

```
ImportError: attempted relative import with no known parent package.
```

The reason for the relative import with no known parent package error is because **package** is set to None, and it needs to be set to something!

If you don't want to use `python -m` to specify a module or package as the main program then add this line to the top of your script when you need it:

`__package__ = __import__("config").infer_package(__file__)`

As a general rule, use explicit relative imports when you are working within the same package, and use absolute imports for external packages.

Says David M. Beazley and he's probably right. See Modules and Packages: Live and Let Die! - PyCon 2015 [1].

Relative imports not only leave you free to rename your package later without changing dozens of internal imports, but they can help with circular imports or namespace packages, because they do not send Python "back to the top" to start the search for the next module all over again from the top-level namespace.

[1] https://www.youtube.com/watch?v=0oTh1CXRaQ0
