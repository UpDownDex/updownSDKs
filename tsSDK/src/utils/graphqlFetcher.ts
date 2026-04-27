import fetch from "cross-fetch";

export default async function graphqlFetcher<T>(
  endpoint: string,
  query: string,
  variables?: object
): Promise<T | undefined> {
  try {
    const response = await fetch(endpoint, {
      body: JSON.stringify({ query, variables }),
      headers: { "Content-type": "application/json" },
      method: "POST",
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error: ${response.status} - ${errorText}`);
    }

    const json = await response.json();

    // Check for GraphQL errors
    if (json.errors) {
      throw new Error(`GraphQL errors: ${JSON.stringify(json.errors)}`);
    }

    return json.data;
  } catch (error: any) {
    throw new Error(`Error fetching GraphQL query: ${error.message || error}`);
  }
}
