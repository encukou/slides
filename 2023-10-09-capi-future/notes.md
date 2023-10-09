I'd love to hear your opinions on the following train of thought about possible future of the C-API.


Premise: **CPython should support native extensions written in non-C languages.**

We want Python to stay a great “glue” language. For that, we want it to have a great interface to other compiled languages.
Currently, C/C++ is special is because CPython is written in C. And so, the API includes stuff that makes life easy for a C programmer, but doesn't necessarily help e.g. Cython, Rust bindings, or `ctypes`. That stuff is obviously important for us, and many other users, but not everyone. Our API should be usable without it.


IMO we should have:

- A *language-agnostic* interface to everything Python can do, composed of simple functions and types with clear rules, which is easy for other languages to wrap.
- A *C-specific API layer* that we treat as one of many possible language-specific layers. At least conceptually: C/C++ support will always be a bit special because:
    - it's shipped with CPython itself
    - it can include optimizations that aren't possible in other language-specific wrappers -- like infine functions.


This corresponds roughly to the [ABI/API distinction](https://github.com/markshannon/New-C-API-for-Python/blob/main/DesignRules.md#abi-functions-should-be-efficient-api-functions-easy-to-use) in Mark's [New C-API proposal](https://github.com/markshannon/New-C-API-for-Python/), where API functions are wrappers that are easy to use (implicitly: easy to use *in C*).
It also roughly corresponds the current limited/“unlimited” API.

The three distinctions (language-agnostic/C-specific, fast/ergonomic, unstable/stable) don't agree 100%, but IMO, they're similar enough that we should merge them, getting:

- A language-agnostic, ABI-stable layer, which isn't necessarily ergonomic for humans to use, but it is easy to generate wrappers for it
- Competing layers on top of that:
  - A C-specific API layer that's easy to use in C, and can use implementation details that can change in every version
  - A “limited C API” layer that trades ABI stability for reduced performance
  - Many possible third-party language bindings and code generators


Before discussing how to get there from what we have now: does this sound like something we should strive for?


---

¹ `ctypes`? Is that a joke? Not entirely: it's a useful proxy for other “language bindings”. If something's hard to use in `ctypes`, it's probably hard for Go, Rust or Java as well. Thinking about ctypes can bring us closer to the “rule of threes” principle for interface design: if the base layer is written for three different things sitting on top, adding more should be easy. In our case, “full” and “limited” C-specific API, and ctypes.




---

I see two primary roles in the C-API:

- CPython internals
- Enabling extension modules (in C or otherwise)



We want Python to stay a great “glue” language. For that, we want it to have a great interface to other compiled languages.
That's one of the primary roles of the C API (along with its use in CPython internals).


Languages other than C/C++ don't have a C preprocessor. They don't have access to header files -- no macros, no inline functions

The ABI is our API, and we should treat it as such



And while C is the *lingua franca* of such interfaces -- every relevant language has a C FFI -- it's not perfect. We need to restrict the features we use
For an in-depth and *very* opinionated article on this topic, see [C Isn't A Programming Language Anymore](https://faultlore.com/blah/c-isnt-a-language/).


-----------------------------------------------------------

Thanks for the list of problems, Irit.

My presentation will be opinionated.
I'll concentrate on what I think we should do, and -- in the interest of time -- I won't cover all the details about why we should do it. Sorry if it seems like my suggestions aren't backed by reasons.
After I'm done, we can talk all week about the requirements, advantages and costs of doing or not doing these things.

I'll start by a few things I think would make good goals. Let me know if you disagree with any of these.

- First-class support native extensions written in non-C languages
  - The C-specific parts of the C-API should be a layer on top of a language-agnostic API.
    It should be easy to build such a layer for any other language -- rather than undo decisions that only make sense in C.

- The ABI is our interface.
  - Other languages don't have the C compiler. They directly wrap whatever is exported from `libpython`.
    They can't *use* macros or inline functions: rather, they *reimplement* them.

    One example to think about:

    `PyObject_CallMethod` is a macro that calls the `_PyObject_CallMethod_SizeT`.

    It's also an exported function that should not be used.

    This switch is "transparent" if you use the C preprocessor. If not, it is not obvious at all. And since it's meant to be transparent, it's not documented.

    (Luckily for this case, varargs functions are tricky, so people using other languages probably need to study the headers anyway.)

    How do we not make this blunder again? We think of the ABI -- the exported symbols -- as our interface.

- The interface should be stable

  Any time users need to change their working code, we have failed.
  It's a reason to abandon their library, or Python altogether.

  Even if the fix is simple. (For example: include this compatibility header! ... in C)

So, this is where I'm starting from.
I believe CPython needs to do this. It would be hard to build this on top of CPython as a third-party library.

I'm not saying these should be our #1 priorities, but I hope we can get a general agreement that it would be a good direction.
Interestingly, there are other goals of a similar type, which tend to guide us toward similar solutions as what I'll explain later:

- We need "tiers" with different stability/performance trade-offs
- It should be possible for other Python implementations to provide the API
  - BTW, thanks to HPy, we know what's needed for that!
  - BTW, it doesn't need to be a Python implementation -- Python's object model is great even without the language ;P

Overhaul?

- Do we do an overhaul -- revise everything, under a new naming convention? And implement the old API on top of this?
  Or do we only apply new guidelines to new functions?

  I assume an overhaul. Let's see what that would look like, and then talk about whether it's worth it.

Specific suggestions:

- We provide two "layers". 
  Mark's proposal calls them "ABI functions" and "API functions", which is confusing, so I'll call them:

  - Python Native Interface:
    - performant
    - complete (provides all necessary building blocks)
    - *not* ergonomic: meant as a base for another layer (C-API, Cython, other language bindings)
    - Unwieldy names that encode argument types
    - "ABI only" -- no C macros

  - Python C API:
    - ergonomic (for C/C++)
    - used for most of CPython, and all stdlib extensions
    - macros & inline functions
    - two modes, selectable at build time:
        - "Stable ABI": everything is a *very* thin wrapper around the native interface
        - "CPython version-specific API": implementations may reach directly into CPython the internals
          - for example: an assert that a function never raises (visible to the user's *compiler* -> compiler skips error handling)
    - the API of these two modes is exactly the same; you only make stability/performance trade-off at build time
    - "Stable ABI" mode autogenerated from a description language
      - limits the available C features
      - allows easily auto-generating wrappers in other languages

  - Unstable C-API -> Additions to the "version-specific API" that can't promise ABI stability

  - Legacy API: The current API, built on top of the lower layers.
    - Eventually moved to a separate project like `pythoncapi-compat`

- Regularity

  - Each function follows the guidelines, strictly and blindly
  - We expect many exceptions to that rule are, but these must:
      - be clearly marked in the name, to avoid misuse
        - `Py_GetNone_Borrow()` -> returns None, which I don't need to decref
      - be an *alternative* to API that follows the rules
        - `Py_GetNone()` -> returns None, which I *do* need to free (even if that is unnecessary in the current implementation)

- Native Interface

  - The native interface consists of:

    - Functions that take & return the following types
      - Fundamental types (`size_t`, `int`)
      - Opaque structs
      - Blueprint structs (see below)
      - Simple interop structs (`Py_buffer` is borderline)
      - Pointers & arrays of the above
    - Simple constants (as macros)
    - Feature flag macros

  - And not of

    - Macros, except:
      - simple constants
      - feature flags (e.g. HAVE_FORK)
    - Bit fields (use integral types and maskks/shifts instead)
    - Enums (use non-negative `int` values)
    - Static inline functions

  - The following can be used as *alternatives*:

    - C-specific types (`short int`)
    - Varargs functions

- Blueprint structs

  Think `PyModuleDef`, `PyType_Spec`, `PyConfig`, etc.

  - versioned (somehow, see later)
  - read-once
    - only valid for the duration of the call
      -> Python needs to *copy everything out*
      -> we don't care if they're static or on the heap
    - if copying is too expensive, there should be an *optional explicit flag* by which the user promises that something is constant & static (e.g. a name or docstring)
  - extensible
    - include an array of "slots"; unlike the current slots they
      - are strongly typed
      - can be marked as optional (Python ignores the slot if it's unknown)

- The API never returns function pointers

  - You can pass a "callback" function pointer to CPython (e.g. your implementation of `tp_add`), but you can *never get it back*
  - Later versions of Python could need a different signature, and generate a trampoline when you use the old signature.
    - user code that does `Py_GetTpAdd(...)(a, b)` will then *fail* on all objects that use the new signature!
  - Instead, there should be functions to:
    - *call* the callback with a specific signature (for newer signatures, Python will fill in defaults)
    - *compare* the callback with the given pointer (does this object do addition the same way as my superclass? If yes I can optimize!)
      - the comparison "unwraps" any trampolines

- The context

  Every function takes a *context* as first argument. Think today's "thread state".

  - Limited context (e.g. for destructors)
  - Easily distinguishing pre-init API (`Py_InitializeFromConfig` takes no context => can't create objects or raise exceptions)
  - More possible tricks -- see the HPy talk later

- Error handling

  - All functions must be able to signal failure (by raising an exception, if possible).
    - This lets us deprecate the function in the future -- `DeprecationWarning` with `-Wall` raises.
    - functions that currently don't raise should be implemented as macros/inline functions that `assert(result > 0)` or `assert(result)`. This lets the *compiler* omit the users' error handling path, and it's easy to remove when an error path appears.

  - functions can return:
    - `int`:
      - `-1`: iff an exception was raised
      - non-negative values: "success" (and other cases where an exception was not raised)
        - `0` for a "lesser" result, `1` for a "greater" result
      - `-2` and less: Not used
    - Object pointer:
      - `NULL` iff an exception was raised
      - valid object otherwise
    - If `-1` or `NULL` is a valid result, the function must take and fill a "result" argument, e.g.
        `int PyLong_ToInt(PyLongObject *obj, int *result)`

        The result should be set to `NULL`/`0` on error. (to avoid people relying on it being unchanged)

  - Functions that can be called before Python is initialized obviously; can't raise exceptions. These must use `PyStatus`.

- Type checking

  `PyListObject*` or `PyObject*`?

  - PNI: strongly typed
  - C-API: Casting & error checking, fails *with exception* on wrong types
  - C-API: if it's really auto-generated, we can use *C11 _Generic selection* and *C++ overloads* for casts..........

- NULL handling

  - PNI: assumes "in" pointers are non-NULL
  - C-API: asserts "in" pointers are not NULL

  - I'd prefer that "result" pointers (ones the function fills in) can be NULL

- Borrowed references

  - Arguments are borrowed from the caller
  - Return values are never borrowed
    - exceptions to that rule must always specify what is being borrowed from -- a tuple? the interpreter?

- String handling

  - Any `char*` needs a "lifetime" -- 
  - Strings `char*` and length
  - NUL-terminated strings are strictly a C-specific convenience (but may need ABI symbols to avoid an extra strlen)

## Legacy Integer Types

IMO, `abi4` should use `size_t`/`ssize_t`/`int`, and sized types `int32_t`.

*NOT* `long` (unless in C-specific API like `PyLong_AsLong`).

Migration path draft:

- `int` becomes `int_32_t` where appropriate
- On platforms where `sizeof(int) != sizeof(int32_t)`, we have broken ABI stability


## WHAT NOT TO CHANGE (YET)

The new API must be flexible enough so we can make the following changes
incrementally in the future.

- Class definition mechanism
- Object layout
- Slot overhaul


I have *many* ideas there, and I'd like to:

- if you can sink the time into *this* and not help with *Native Interface*/*abi4*:
  - ask me and I'll fill you in
- otherwise
  - let's postpone all discussions on this topic


## Naming

We can reuse current naming for the C-API (to improve backward compatibility); or come up with a new one (to clean up all the `ObjectRefExWithError` prefixes).

We should *never* reuse the name of a function that was deprecated and removed. That's just too confusing. Old docs never die.

We need a new naming scheme for the Native Interface.

We can make it ugly -- this stuff is for machines. Let's encode argument types in it, á la C++ name mangling.

- `PyNI_<name>_<args>_<ret>`

e.g.

- `PyObject *PyNI_DictGet_OdS_O(PyDictObject *o, char* name)`

with names like:

- `O` = object
- `Od` = dict object
- `Ods` = stolen dict object
- `I`, `B` = int, bool
- `S1`, `S2` = struct


## Versioning

There are 3 relevant version numbers:

- The CPython used to build the extension
- The lowest CPython that should be able to load the extension
- The CPython version for which the codebase was *started* or last "modernized" -- older *deprecated* API is unavailable


The first 2 should 
- go in the wheel tag
- be checked at load time (`PyInit_*`)

The last one is build-only.

### Deprecation

How long should we keep support for old API?

- `3.x` ABI should support all versions in active support at `3.x.0rc1`
- *But* old versions are only dropped if necessary. There will usually be someone willing to jump through hoops to keep old API alive
  - we should let them do that if it doesn't block others
  - give them enough heads-up time


## Struct Versioning

Here's an idea: rather than put a version *in structs*, version the *functions* that take them.

- `typedef struct {...} PyNI_ModuleDef_v1`
- `typedef struct {..., ...} PyNI_ModuleDef_v2`
- Native interface: `PyModuleObject* PyNI_ModuleFromDef_S2_Om(PyModuleDef_v2* def)`

\+

- `typedef PyModuleDef_v2 PyModuleDef`
- `#define PyModule_FromDef PyNI_ModuleFromDef_S2_Om` (roughly)
- C-API: `PyModule_FromDef(PyModuleDef* def)`

Why?

- Can deal with structs that aren't versioned now (!)
- Cleaner C-API
- Incompatible extensions fail at link time
- Binary extensions can be examined for compatibility statically (platform-specific)

Why not?

- Assumes `0`/`NULL` is a good default for new fields
- More symbols to export
- Incompatible extensions fail at link time


## Who does this?

I hope my employer gives me 50% full-time for 6 months to write enough Native Interface to cover the current Limited API. 

Depending on volunteer availability, I can act as a manager or do it myself.
