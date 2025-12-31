import TextSearchForm from "./text-search/TextSearchForm.tsx";
import ImageDropper from "./image-match/ImageDropper.tsx";

export default function ImageSearchContainer () {

    return (
        <>
            <ImageDropper/>
            <TextSearchForm />
        </>
    );
}