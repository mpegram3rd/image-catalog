export interface ImageMatchResult {
    image_path: string;
    description: string;
}

export interface ImageSearchResults {
    results: ImageMatchResult[];
}
