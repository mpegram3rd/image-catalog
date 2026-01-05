import type {Dispatch, SetStateAction} from "react";
import type {ImageSearchResults} from "../models/ImageSearchResults.ts";

export default interface ImageSearchContainerProps {
    setSearchResults: Dispatch<SetStateAction<ImageSearchResults>>;
    setLoading: Dispatch<SetStateAction<boolean>>;
}

