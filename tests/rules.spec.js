// The Firestore security rules, tested against the emulator. Runs only under npm run test:all.
import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { initializeTestEnvironment, assertFails, assertSucceeds } from "@firebase/rules-unit-testing";
import { doc, getDoc, setDoc, updateDoc, deleteDoc, collection, getDocs, serverTimestamp } from "firebase/firestore";

const HOST = process.env.FIRESTORE_EMULATOR_HOST;
test.skip(!HOST, "Runs only under npm run test:all");

let env;
test.beforeAll(async () => {
  const [host, port] = HOST.split(":");
  env = await initializeTestEnvironment({
    projectId: "demo-mcu",
    firestore: { host, port: Number(port), rules: readFileSync(new URL("../firebase/firestore.rules", import.meta.url), "utf8") },
  });
});
test.afterAll(() => env?.cleanup());

/* Tests run side by side against one emulator, so every test gets people of its own. */
let n = 0;
const someone = () => `user-${process.pid}-${++n}-${Math.random().toString(36).slice(2, 8)}`;
const google = { firebase: { sign_in_provider: "google.com" } };
const as = (uid, token = google) => env.authenticatedContext(uid, token).firestore();
const signedOut = () => env.unauthenticatedContext().firestore();
const userDoc = (db, uid) => doc(db, "users", uid);
const valid = (extra = {}) => ({ schema: 1, watched: { 0: { on: true, at: Date.now() } }, updatedAt: serverTimestamp(), ...extra });
const seed = (uid, data = valid()) => env.withSecurityRulesDisabled(ctx => setDoc(userDoc(ctx.firestore(), uid), data));

test.describe("your own document", () => {
  test("you can create, read, update and delete it", async () => {
    const me = someone(), db = as(me);
    await assertSucceeds(setDoc(userDoc(db, me), valid()));
    await assertSucceeds(getDoc(userDoc(db, me)));
    await assertSucceeds(updateDoc(userDoc(db, me), { "watched.21": { on: true, at: Date.now() }, updatedAt: serverTimestamp() }));
    await assertSucceeds(deleteDoc(userDoc(db, me)));
  });

  test("you can save your theme, spoiler setting and route", async () => {
    const me = someone();
    await assertSucceeds(setDoc(userDoc(as(me), me), valid({ prefs: { theme: "light", spoilers: true, route: "doomsday" } })));
    await assertSucceeds(setDoc(userDoc(as(me), me), valid({ prefs: { theme: "dark" } })));
  });

  test("a full list fits, up to 400 titles", async () => {
    const me = someone(), watched = Object.fromEntries(Array.from({ length: 400 }, (_, i) => [i, { on: true, at: 1 }]));
    await assertSucceeds(setDoc(userDoc(as(me), me), valid({ watched })));
  });
});

test.describe("other people's documents", () => {
  test("you can't read someone else's", async () => {
    const me = someone(), them = someone();
    await seed(them);
    await assertFails(getDoc(userDoc(as(me), them)));
  });

  test("you can't write or delete someone else's", async () => {
    const me = someone(), them = someone(), fresh = someone();
    await seed(them);
    await assertFails(setDoc(userDoc(as(me), them), valid()));
    await assertFails(updateDoc(userDoc(as(me), them), { "watched.1": { on: true, at: 1 }, updatedAt: serverTimestamp() }));
    await assertFails(deleteDoc(userDoc(as(me), them)));
    await assertFails(setDoc(userDoc(as(me), fresh), valid()));
  });

  test("you can't list everyone's documents", async () => {
    const me = someone();
    await seed(me);
    await assertFails(getDocs(collection(as(me), "users")));
  });
});

test.describe("who can get in", () => {
  test("signed-out visitors can't read or write anything", async () => {
    const them = someone();
    await seed(them);
    await assertFails(getDoc(userDoc(signedOut(), them)));
    await assertFails(setDoc(userDoc(signedOut(), them), valid()));
    await assertFails(getDocs(collection(signedOut(), "users")));
  });

  test("only Google sign-in counts", async () => {
    const me = someone();
    for (const provider of ["password", "anonymous", "emailLink"]){
      const db = as(me, { firebase: { sign_in_provider: provider } });
      await assertFails(setDoc(userDoc(db, me), valid()));
    }
    await seed(me);
    await assertFails(getDoc(userDoc(as(me, { firebase: { sign_in_provider: "password" } }), me)));
  });

  test("nothing outside users can be read or written", async () => {
    const me = someone(), db = as(me);
    await assertFails(setDoc(doc(db, "notes", me), { hello: 1 }));
    await assertFails(getDoc(doc(db, "notes", me)));
    await assertFails(setDoc(doc(db, "users", me, "extra", "x"), { hello: 1 }));
  });
});

test.describe("what a document may hold", () => {
  const refused = {
    "an unknown field": valid({ admin: true }),
    "no schema": (({ schema, ...d }) => d)(valid()),
    "no watched list": (({ watched, ...d }) => d)(valid()),
    "a schema the page doesn't know": valid({ schema: 2 }),
    "a watched list that isn't a map": valid({ watched: [0, 1, 2] }),
    "more than 400 titles": valid({ watched: Object.fromEntries(Array.from({ length: 401 }, (_, i) => [i, { on: true, at: 1 }])) }),
    "a time the browser made up": valid({ updatedAt: new Date() }),
    "prefs that aren't a map": valid({ prefs: "dark" }),
    "an unknown theme": valid({ prefs: { theme: "neon" } }),
    "a spoiler setting that isn't on or off": valid({ prefs: { spoilers: "yes" } }),
    "an unknown setting": valid({ prefs: { fontSize: 20 } }),
    "a route name longer than 40 characters": valid({ prefs: { route: "x".repeat(41) } }),
  };
  for (const [what, data] of Object.entries(refused))
    test(`${what} is refused`, async () => {
      const me = someone();
      await assertFails(setDoc(userDoc(as(me), me), data));
    });

  test("an update is checked against the whole document it leaves behind", async () => {
    const me = someone(), db = as(me);
    await assertSucceeds(setDoc(userDoc(db, me), valid()));
    await assertFails(updateDoc(userDoc(db, me), { admin: true, updatedAt: serverTimestamp() }));
    await assertFails(updateDoc(userDoc(db, me), { "watched.5": { on: true, at: 1 } }));
    await assertFails(updateDoc(userDoc(db, me), { "prefs.theme": "neon", updatedAt: serverTimestamp() }));
    let saved;
    await env.withSecurityRulesDisabled(async ctx => { saved = (await getDoc(userDoc(ctx.firestore(), me))).data(); });
    expect(Object.keys(saved.watched)).toEqual(["0"]);
  });
});
