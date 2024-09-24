import { gql } from "@apollo/client";
// augment mutation
// GraphQL Mutation
export const AUGMENT_MUTATION = gql`
  mutation AugmentQuestion($id: ID!, $original: String!, $refinement: String!) {
    augmentQuestion(id: $id, original: $original, refinement: $refinement) {
      refinedContent
    }
  }
`;

