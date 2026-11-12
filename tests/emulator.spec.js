import { test, expect } from "@playwright/test";

test("the emulator refuses a signed-out write", async ({ request }) => {
  const host = process.env.FIRESTORE_EMULATOR_HOST;
  test.skip(!host, "Runs only under npm run test:all");
  const url = `http://${host}/v1/projects/demo-mcu/databases/(default)/documents/users?documentId=someone`;
  expect((await request.post(url, { data: { fields: {} } })).status()).toBe(403);
  // The emulator's admin token skips the rules, which proves the 403 came from the rules and not a wrong address.
  expect((await request.post(url.replace("someone", "admin-check"), { data: { fields: {} }, headers: { authorization: "Bearer owner" } })).status()).toBe(200);
});
