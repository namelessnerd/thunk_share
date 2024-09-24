import React, { useRef, useState } from 'react';
import './AugmentWithAI.css'; // New styles as seen above
import SetToneButton from './SetToneButton';
import AugmentButton from './AugmentButton';
import useFieldApi from "components/forms/hooks/use-field-api";
import FormFieldGrid from "components/forms/hoc/form-field-grid";
import PropTypes from "prop-types";
import { validationError } from "components/forms/utils/helpers";
import { useMutation } from '@apollo/client';
import { AUGMENT_MUTATION } from "./constants";

const AugmentWithAI = (props) => {
  const [augmentQuestion, { data, loading, error }] = useMutation(AUGMENT_MUTATION);
  const { initialValues } = props;
  const { id, title, aiExplain } = initialValues || {};
  const {
    input,
    isReadOnly,
    isDisabled,
    placeholder,
    isRequired,
    helperText,
    description,
    validateOnMount,
    meta,
    inputProps,
    FormFieldGridProps,
    inputLabel,
    ...rest
  } = useFieldApi(props);

  const invalid = validationError(meta, validateOnMount);
  const textAreaRef = useRef(null);
  const userEditRef = useRef(null);

  // Local state to control the text in both textareas
  const [questionText, setQuestionText] = useState(title || "");
  const [userEditText, setUserEditText] = useState("");
  

  const handleTextChange = (event) => {
    const textarea = textAreaRef.current;
    textarea.style.height = "auto"; 
    textarea.style.height = `${textarea.scrollHeight}px`;
    input.onChange(event);
    setQuestionText(event.target.value);
  };

  const handleToneSelect = (selectedTone) => {
    if (userEditRef.current) {
      userEditRef.current.value = `Refine this text to be more ${selectedTone.toLowerCase()}.`;
    }
  };

  const handleAugmentClick = async () => {
    const refinement = userEditRef.current ? userEditRef.current.value.trim() : '';
    let original = `Question Generated: ${title}; Eligibility Criteria: ${aiExplain}`;
  
    if (!refinement) {
      console.log("User Input is required.");
      return;
    }
  
    try {
      const response = await augmentQuestion({
        variables: { id, original, refinement },
      });
  
      if (response?.data?.augmentQuestion?.refinedContent) {
        console.log(response.data.augmentQuestion.refinedContent)
        setQuestionText(response.data.augmentQuestion.refinedContent);
        input.onChange(response.data.augmentQuestion.refinedContent);
      }
    } catch (err) {
      console.error('Error calling mutation:', err);
    }
  };

  const toneOptions = ['Empathetic', 'Simple', 'Friendly'];

  return (
    <FormFieldGrid {...FormFieldGridProps}>
      {inputLabel && <label>{inputLabel}</label>}
      <div className="augment-container">
        <div className="input-group" style={{ marginBottom: '0px' }}>
          <div className="input-container">
            <textarea
              ref={textAreaRef}
              value={questionText}
              onChange={handleTextChange}
              className="text-box top-box"
              placeholder="Enter question text"></textarea>
          </div>
          <div className="divider"></div>
          <div className="input-container">
            <textarea 
              className="text-box bottom-box"
              ref={userEditRef}
              placeholder="Use TrialXAI to simplify or adjust the tone.">
              </textarea>
          </div>
        </div>
        <div className="buttons-container">
          <SetToneButton toneOptions={toneOptions} onToneSelect={handleToneSelect} />
          <AugmentButton onClick={handleAugmentClick} />
        </div>
        {/* Show validation errors, warnings, or helper text */}
        {invalid || ((meta.touched || validateOnMount) && meta.warning) || helperText || description}
      </div>
    </FormFieldGrid>
  );
};

AugmentWithAI.defaultProps = {
  inputLabel: null,
};

AugmentWithAI.propTypes = {
  inputLabel: PropTypes.string,
};

export default AugmentWithAI;

