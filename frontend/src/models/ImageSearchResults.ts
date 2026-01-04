export interface ImageMatchResult {
    image_path: string;
    description: string;
    thumbnail: string;
    distance: number;
}

export interface ImageSearchResults {
    results: ImageMatchResult[];
}
